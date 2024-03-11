"""Added date to arts, categories

Revision ID: 1e3a0e039d62
Revises: ecd7e763d60b
Create Date: 2024-03-11 15:26:13.066395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e3a0e039d62'
down_revision: Union[str, None] = 'ecd7e763d60b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_table('art_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('art_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['art_id'], ['arts.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'art_id')
    )
    op.add_column('arts', sa.Column('date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('arts', 'date')
    op.drop_table('art_categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###