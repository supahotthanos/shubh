"""Initial schema — create every table defined by SQLAlchemy models.

Generated without `--autogenerate` because the models are stable; the simplest
correct thing is to run `Base.metadata.create_all` through Alembic's connection
so that Alembic records the revision while matching the ORM exactly.
"""
from __future__ import annotations

from alembic import op

from app.core.database import Base
from app import models  # noqa: F401 — registers all mappers

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
