"""add domain relevance_score and ig_drafts table

Revision ID: 002
Revises: 43db6c86d1d4
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '002'
down_revision = '43db6c86d1d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A) Extend news table
    op.add_column('news', sa.Column('domain', sa.Text(), nullable=False, server_default='real_estate'))
    op.add_column('news', sa.Column('relevance_score', sa.Integer(), nullable=True))
    op.create_index('ix_news_domain', 'news', ['domain'], unique=False)
    op.create_index('ix_news_relevance_score', 'news', ['relevance_score'], unique=False)

    # B) Create ig_drafts table
    op.create_table(
        'ig_drafts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('news_id', UUID(as_uuid=True), nullable=False),
        sa.Column('hook', sa.Text(), nullable=True),
        sa.Column('carousel_slides', JSONB(), nullable=False),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('hashtags', JSONB(), nullable=True),
        sa.Column('cta', sa.Text(), nullable=True),
        sa.Column('source_line', sa.Text(), nullable=False),
        sa.Column('disclaimer', sa.Text(), nullable=True),
        sa.Column('tone', sa.Text(), nullable=False, server_default='neutral'),
        sa.Column('language', sa.Text(), nullable=False, server_default='es'),
        sa.Column('status', sa.Text(), nullable=False, server_default='DRAFT'),
        sa.Column('editor_notes', sa.Text(), nullable=True),
        sa.Column('variant_of_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_of_id'], ['ig_drafts.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_ig_drafts_news_id', 'ig_drafts', ['news_id'], unique=False)
    op.create_index('ix_ig_drafts_status', 'ig_drafts', ['status'], unique=False)
    op.create_index('ix_ig_drafts_created_at', 'ig_drafts', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_ig_drafts_news_id', table_name='ig_drafts')
    op.drop_index('ix_ig_drafts_created_at', table_name='ig_drafts')
    op.drop_index('ix_ig_drafts_status', table_name='ig_drafts')
    op.drop_table('ig_drafts')

    op.drop_index('ix_news_relevance_score', table_name='news')
    op.drop_index('ix_news_domain', table_name='news')
    op.drop_column('news', 'relevance_score')
    op.drop_column('news', 'domain')
