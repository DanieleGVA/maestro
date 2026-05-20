"""Unit tests for the three-level content cache (content/cache.py).

All Redis and DB calls are mocked.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.content.cache import CACHE_TTL_SECONDS, ContentCache, _cache_key


class TestCacheKey:
    def test_deterministic(self) -> None:
        """Same inputs produce same key."""
        k1 = _cache_key("stu-1", "node-1", "review")
        k2 = _cache_key("stu-1", "node-1", "review")
        assert k1 == k2

    def test_different_inputs_different_keys(self) -> None:
        k1 = _cache_key("stu-1", "node-1", "review")
        k2 = _cache_key("stu-2", "node-1", "review")
        assert k1 != k2

    def test_is_sha256_hex(self) -> None:
        k = _cache_key("a", "b", "c")
        assert len(k) == 64  # SHA-256 hex digest


class TestContentCacheL1:
    @pytest.fixture
    def cache(self) -> ContentCache:
        return ContentCache()

    @pytest.mark.asyncio
    async def test_get_l1_cache_hit(self, cache: ContentCache, mock_redis: AsyncMock) -> None:
        """L1 should return cached content when present."""
        content = {"blocks": []}
        mock_redis.get = AsyncMock(return_value=json.dumps(content))
        cache._redis = mock_redis

        result = await cache.get_l1("stu-1", "node-1", "review")
        assert result == content

    @pytest.mark.asyncio
    async def test_get_l1_cache_miss(self, cache: ContentCache, mock_redis: AsyncMock) -> None:
        """L1 should return None when content is not cached."""
        mock_redis.get = AsyncMock(return_value=None)
        cache._redis = mock_redis

        result = await cache.get_l1("stu-1", "node-1", "review")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_l1_stores_with_ttl(self, cache: ContentCache, mock_redis: AsyncMock) -> None:
        """L1 set should store with CACHE_TTL_SECONDS."""
        cache._redis = mock_redis
        content = {"data": "test"}

        await cache.set_l1("stu-1", "node-1", "review", content)

        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[1] == CACHE_TTL_SECONDS

    @pytest.mark.asyncio
    async def test_l1_graceful_on_redis_failure(self, cache: ContentCache) -> None:
        """L1 should return None and not raise on Redis failure."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=ConnectionError("Redis down"))
        cache._redis = mock_redis

        result = await cache.get_l1("stu-1", "node-1", "review")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_l1_graceful_on_redis_failure(self, cache: ContentCache) -> None:
        """L1 set should not raise on Redis failure."""
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=ConnectionError("Redis down"))
        cache._redis = mock_redis

        # Should not raise
        await cache.set_l1("stu-1", "node-1", "review", {"data": "test"})


class TestContentCacheL2:
    @pytest.fixture
    def cache(self) -> ContentCache:
        return ContentCache()

    @pytest.mark.asyncio
    async def test_get_l2_hit(
        self, cache: ContentCache, mock_db_session: AsyncMock
    ) -> None:
        """L2 should return content from DB."""
        content = {"blocks": []}
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, idx: content if idx == 0 else None
        mock_result = MagicMock()
        mock_result.first.return_value = mock_row
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await cache.get_l2(
            mock_db_session,
            student_pseudo_id="stu-1",
            node_id="node-1",
            content_type="review",
        )
        assert result == content

    @pytest.mark.asyncio
    async def test_get_l2_miss(
        self, cache: ContentCache, mock_db_session: AsyncMock
    ) -> None:
        """L2 should return None when not in DB."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await cache.get_l2(
            mock_db_session,
            student_pseudo_id="stu-1",
            node_id="node-1",
            content_type="review",
        )
        assert result is None


class TestContentCacheL3:
    @pytest.mark.asyncio
    async def test_l3_placeholder_returns_none(self) -> None:
        """L3 placeholder should always return None in MVP."""
        cache = ContentCache()
        result = await cache.get_l3("node-1", "review")
        assert result is None


class TestContentCacheUnified:
    @pytest.fixture
    def cache(self) -> ContentCache:
        return ContentCache()

    @pytest.mark.asyncio
    async def test_unified_returns_l1_first(
        self, cache: ContentCache, mock_db_session: AsyncMock, mock_redis: AsyncMock
    ) -> None:
        """Unified get should check L1 first."""
        content = {"from": "l1"}
        mock_redis.get = AsyncMock(return_value=json.dumps(content))
        cache._redis = mock_redis

        result = await cache.get(
            mock_db_session,
            student_pseudo_id="stu-1",
            node_id="node-1",
            content_type="review",
        )
        assert result == content

    @pytest.mark.asyncio
    async def test_unified_falls_through_to_l2(
        self, cache: ContentCache, mock_db_session: AsyncMock, mock_redis: AsyncMock
    ) -> None:
        """When L1 misses, unified get should check L2."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock()
        cache._redis = mock_redis

        l2_content = {"from": "l2"}
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, idx: l2_content if idx == 0 else None
        mock_result = MagicMock()
        mock_result.first.return_value = mock_row
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await cache.get(
            mock_db_session,
            student_pseudo_id="stu-1",
            node_id="node-1",
            content_type="review",
        )
        assert result == l2_content
        # Should also populate L1
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_unified_returns_none_when_all_miss(
        self, cache: ContentCache, mock_db_session: AsyncMock, mock_redis: AsyncMock
    ) -> None:
        """When all levels miss, return None."""
        mock_redis.get = AsyncMock(return_value=None)
        cache._redis = mock_redis

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await cache.get(
            mock_db_session,
            student_pseudo_id="stu-1",
            node_id="node-1",
            content_type="review",
        )
        assert result is None
