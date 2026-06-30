"""Add hero text fields to site settings

Revision ID: 2a3b4c5d6e7f
Revises: 090f99eedf14
Create Date: 2026-06-30 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '2a3b4c5d6e7f'
down_revision = '090f99eedf14'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hero_title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('hero_subtitle', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('hero_btn_text', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('hero_btn_url', sa.String(length=500), nullable=True))


def downgrade():
    with op.batch_alter_table('site_settings', schema=None) as batch_op:
        batch_op.drop_column('hero_btn_url')
        batch_op.drop_column('hero_btn_text')
        batch_op.drop_column('hero_subtitle')
        batch_op.drop_column('hero_title')
