"""Add SEO fields to site_settings

Revision ID: 7f8e9d0c1b2a
Revises: 2a3b4c5d6e7f
Create Date: 2026-06-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f8e9d0c1b2a'
down_revision = '2a3b4c5d6e7f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta_title', sa.String(length=255), nullable=True, server_default='John & Eniola Consultancy'))
        batch_op.add_column(sa.Column('meta_description', sa.Text(), nullable=True, server_default='Your trusted partner in financial excellence.'))
        batch_op.add_column(sa.Column('og_image', sa.String(length=500), nullable=True, server_default='/static/images/og-default.jpg'))
        batch_op.add_column(sa.Column('google_analytics_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('google_tag_manager_id', sa.String(length=50), nullable=True))


def downgrade():
    with op.batch_alter_table('site_settings', schema=None) as batch_op:
        batch_op.drop_column('google_tag_manager_id')
        batch_op.drop_column('google_analytics_id')
        batch_op.drop_column('og_image')
        batch_op.drop_column('meta_description')
        batch_op.drop_column('meta_title')
