"""Add blocked comments table

Revision ID: 4e24bf1e8ad0
Revises: 5b0673a84287
Create Date: 2024-07-18 20:31:15.346748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e24bf1e8ad0'
down_revision: Union[str, None] = '5b0673a84287'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###