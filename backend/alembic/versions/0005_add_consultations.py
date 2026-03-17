"""add consultations table

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 테이블이 이미 존재할 경우(수동 생성 등) user_id nullable 보장
    from sqlalchemy import inspect
    from alembic import op as _op
    bind = op.get_bind()
    if 'consultations' in inspect(bind).get_table_names():
        op.alter_column('consultations', 'user_id', nullable=True)
        return

    op.create_table(
        'consultations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('birth_input', JSONB(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('headline', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('share_token', UUID(as_uuid=True), unique=True, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_consultations_user_id', 'consultations', ['user_id'])
    op.create_index('ix_consultations_created_at', 'consultations', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_consultations_created_at', table_name='consultations')
    op.drop_index('ix_consultations_user_id', table_name='consultations')
    op.drop_table('consultations')
