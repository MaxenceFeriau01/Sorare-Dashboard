"""merge_predictions_and_leagues

Revision ID: 0f2398e664a6
Revises: 37c6ad2f8e70, add_league_field
Create Date: 2025-12-15 16:22:11.484428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f2398e664a6'
down_revision: Union[str, None] = ('37c6ad2f8e70', 'add_league_field')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
