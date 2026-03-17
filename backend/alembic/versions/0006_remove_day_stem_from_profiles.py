"""remove day_stem from profiles

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-17
"""
from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('profiles', 'day_stem')
    op.drop_column('profiles', 'day_branch')
    op.drop_column('profiles', 'day_stem_element')


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column('profiles', sa.Column('day_stem', sa.String(5), nullable=True))
    op.add_column('profiles', sa.Column('day_branch', sa.String(5), nullable=True))
    op.add_column('profiles', sa.Column('day_stem_element', sa.String(5), nullable=True))
