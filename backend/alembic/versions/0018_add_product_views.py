"""add product_views (상품 열람 기록)

Revision ID: 0018
Revises: 0017
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_views",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.String(length=40), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("day_stem", sa.String(length=2), nullable=True),
        sa.Column("age_band", sa.String(length=8), nullable=True),
        sa.Column("gender", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_product_views_product_created", "product_views", ["product_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_product_views_product_created", table_name="product_views")
    op.drop_table("product_views")
