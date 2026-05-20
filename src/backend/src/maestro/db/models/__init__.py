"""SQLAlchemy ORM models. One module per schema (core, kmm, content, audit)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass
