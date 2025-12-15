"""Add league field to players

Revision ID: add_league_field
Revises: 
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_league_field'
down_revision = None  # Remplace par le dernier revision ID si tu en as déjà
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne league à la table players
    op.add_column('players', sa.Column('league_name', sa.String(length=200), nullable=True))
    op.add_column('players', sa.Column('league_id', sa.Integer(), nullable=True))
    op.add_column('players', sa.Column('league_country', sa.String(length=100), nullable=True))
    
    # Ajouter un index pour améliorer les performances de filtrage
    op.create_index(op.f('ix_players_league_name'), 'players', ['league_name'], unique=False)


def downgrade():
    # Supprimer l'index et les colonnes
    op.drop_index(op.f('ix_players_league_name'), table_name='players')
    op.drop_column('players', 'league_country')
    op.drop_column('players', 'league_id')
    op.drop_column('players', 'league_name')