"""Three-level content cache (HLD-003).

L1: Redis in-memory for recent content (TTL 1h)
L2: DB lookup in content.generated_content before regenerating
L3: Batch pre-generation for high-traffic nodes (placeholder MVP)
"""

import hashlib
import json
import logging

import redis.asyncio as redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.config import settings

logger = logging.getLogger(__name__)

# L1 cache TTL
CACHE_TTL_SECONDS = 3600  # 1 hour


def _cache_key(student_pseudo_id: str, node_id: str, content_type: str) -> str:
    """Build a Redis cache key for content."""
    raw = f"content:{student_pseudo_id}:{node_id}:{content_type}"
    return hashlib.sha256(raw.encode()).hexdigest()


class ContentCache:
    """Three-level content caching."""

    def __init__(self) -> None:
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url, decode_responses=True
            )
        return self._redis

    # ------------------------------------------------------------------
    # L1: Redis in-memory cache
    # ------------------------------------------------------------------
    async def get_l1(
        self,
        student_pseudo_id: str,
        node_id: str,
        content_type: str,
    ) -> dict | None:
        """Check L1 (Redis) cache for recent content."""
        try:
            r = await self._get_redis()
            key = _cache_key(student_pseudo_id, node_id, content_type)
            raw = await r.get(key)
            if raw:
                logger.debug("L1 cache hit: %s", key[:16])
                return json.loads(raw)
        except Exception:
            logger.debug("L1 cache unavailable, skipping")
        return None

    async def set_l1(
        self,
        student_pseudo_id: str,
        node_id: str,
        content_type: str,
        content: dict,
    ) -> None:
        """Store content in L1 (Redis) cache."""
        try:
            r = await self._get_redis()
            key = _cache_key(student_pseudo_id, node_id, content_type)
            await r.setex(key, CACHE_TTL_SECONDS, json.dumps(content, default=str))
        except Exception:
            logger.debug("L1 cache write failed, continuing without cache")

    # ------------------------------------------------------------------
    # L2: DB lookup in content.generated_content
    # ------------------------------------------------------------------
    async def get_l2(
        self,
        session: AsyncSession,
        *,
        student_pseudo_id: str,
        node_id: str,
        content_type: str,
    ) -> dict | None:
        """Check L2 (DB) for existing generated content."""
        result = await session.execute(
            text("""
                SELECT content, id
                FROM content.generated_content
                WHERE student_pseudo_id = :pseudo_id
                  AND node_id = :node_id
                  AND content_type = :content_type
                  AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {
                "pseudo_id": student_pseudo_id,
                "node_id": node_id,
                "content_type": content_type,
            },
        )
        row = result.first()
        if row:
            logger.debug("L2 cache hit: node=%s type=%s", node_id, content_type)
            return row[0] if isinstance(row[0], dict) else json.loads(row[0])
        return None

    # ------------------------------------------------------------------
    # L3: Batch pre-generation (placeholder MVP)
    # ------------------------------------------------------------------
    async def get_l3(self, node_id: str, content_type: str) -> dict | None:
        """Check L3 (pre-generated batch content). Placeholder for MVP."""
        # V1: implement batch pre-generation for high-traffic nodes
        return None

    # ------------------------------------------------------------------
    # Unified lookup
    # ------------------------------------------------------------------
    async def get(
        self,
        session: AsyncSession,
        *,
        student_pseudo_id: str,
        node_id: str,
        content_type: str,
    ) -> dict | None:
        """Check all cache levels in order: L1 -> L2 -> L3."""
        # L1
        cached = await self.get_l1(student_pseudo_id, node_id, content_type)
        if cached:
            return cached

        # L2
        cached = await self.get_l2(
            session,
            student_pseudo_id=student_pseudo_id,
            node_id=node_id,
            content_type=content_type,
        )
        if cached:
            # Populate L1 for next request
            await self.set_l1(student_pseudo_id, node_id, content_type, cached)
            return cached

        # L3
        cached = await self.get_l3(node_id, content_type)
        if cached:
            await self.set_l1(student_pseudo_id, node_id, content_type, cached)
            return cached

        return None
