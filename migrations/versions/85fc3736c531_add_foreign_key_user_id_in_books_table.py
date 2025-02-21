"""add foreign key user_id in books table

Revision ID: 85fc3736c531
Revises: 40c9e6de7de1
Create Date: 2025-01-01 19:31:04.011557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '85fc3736c531'
down_revision: Union[str, None] = '40c9e6de7de1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'books', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.drop_column('books', 'user_id')
    # ### end Alembic commands ###
