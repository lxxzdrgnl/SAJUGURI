"""add profile is_representative

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'profiles',
        sa.Column('is_representative', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('profiles', 'is_representative')
