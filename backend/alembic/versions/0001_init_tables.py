"""init tables

Revision ID: 0001
Revises:
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('provider', sa.String(20), nullable=False, server_default='local'),
        sa.Column('social_id', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('birth_time', sa.Time(), nullable=True),
        sa.Column('calendar', sa.String(10), nullable=False, server_default='solar'),
        sa.Column('gender', sa.String(10), nullable=False),
        sa.Column('is_leap_month', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('longitude', sa.Numeric(7, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'shared_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('birth_input', postgresql.JSONB(), nullable=True),
        sa.Column('share_token', postgresql.UUID(as_uuid=True), nullable=False, unique=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('calc_snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('shared_results')
    op.drop_table('refresh_tokens')
    op.drop_table('profiles')
    op.drop_table('users')
