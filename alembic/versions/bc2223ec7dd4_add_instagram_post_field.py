"""add_instagram_post_field

Revision ID: bc2223ec7dd4
Revises: 7559f42308c6
Create Date: 2026-01-07 12:09:52.119399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc2223ec7dd4'
down_revision = '7559f42308c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('news', sa.Column('instagram_post', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('news', 'instagram_post')

