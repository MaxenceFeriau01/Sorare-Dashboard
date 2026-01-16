"""merge heads

Revision ID: 0c1d3a369003
Revises: 0f2398e664a6, add_player_statistics
Create Date: 2025-12-16 20:41:55.241018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c1d3a369003'
down_revision: Union[str, None] = ('0f2398e664a6', 'add_player_statistics')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
