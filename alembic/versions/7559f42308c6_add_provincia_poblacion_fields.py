"""add_provincia_poblacion_fields

Revision ID: 7559f42308c6
Revises: 001_initial
Create Date: 2025-12-09 09:30:50.260341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7559f42308c6'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('news', sa.Column('provincia', sa.String(), nullable=True))
    op.add_column('news', sa.Column('poblacion', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('news', 'poblacion')
    op.drop_column('news', 'provincia')

