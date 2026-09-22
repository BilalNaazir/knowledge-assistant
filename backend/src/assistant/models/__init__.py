"""SQLAlchemy ORM models. Import every model module here, so Alembic's
autogenerate can see the full set of tables through `Base.metadata`.
"""

from assistant.models.base import Base

__all__ = ["Base"]
