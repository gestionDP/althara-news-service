"""add_althara_content_field

Revision ID: 43db6c86d1d4
Revises: bc2223ec7dd4
Create Date: 2026-01-08 09:15:56.144200

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '43db6c86d1d4'
down_revision = 'bc2223ec7dd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('news', sa.Column('althara_content', JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('news', 'althara_content')

