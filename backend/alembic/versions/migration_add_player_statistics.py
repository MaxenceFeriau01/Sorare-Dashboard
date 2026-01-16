"""
Ajout de la table player_statistics pour les statistiques détaillées des joueurs

Revision ID: add_player_statistics
Revises: [previous_revision]
Create Date: 2024-12-16
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_player_statistics'
down_revision = None  # Remplacer par l'ID de la révision précédente
branch_labels = None
depends_on = None


def upgrade():
    # Création de la table player_statistics
    op.create_table(
        'player_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Informations du joueur
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('player_name', sa.String(), nullable=False),
        sa.Column('player_firstname', sa.String(), nullable=True),
        sa.Column('player_lastname', sa.String(), nullable=True),
        sa.Column('player_age', sa.Integer(), nullable=True),
        sa.Column('player_birth_date', sa.Date(), nullable=True),
        sa.Column('player_birth_place', sa.String(), nullable=True),
        sa.Column('player_birth_country', sa.String(), nullable=True),
        sa.Column('player_nationality', sa.String(), nullable=True),
        sa.Column('player_height', sa.String(), nullable=True),
        sa.Column('player_weight', sa.String(), nullable=True),
        sa.Column('player_injured', sa.Boolean(), nullable=True, default=False),
        sa.Column('player_photo', sa.String(), nullable=True),
        
        # Informations de l'équipe
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('team_logo', sa.String(), nullable=True),
        
        # Informations de la ligue
        sa.Column('league_id', sa.Integer(), nullable=True),
        sa.Column('league_name', sa.String(), nullable=True),
        sa.Column('league_country', sa.String(), nullable=True),
        sa.Column('league_logo', sa.String(), nullable=True),
        sa.Column('league_flag', sa.String(), nullable=True),
        sa.Column('season', sa.Integer(), nullable=True),
        
        # Statistiques de jeu
        sa.Column('games_appearences', sa.Integer(), nullable=True, default=0),
        sa.Column('games_lineups', sa.Integer(), nullable=True, default=0),
        sa.Column('games_minutes', sa.Integer(), nullable=True, default=0),
        sa.Column('games_number', sa.Integer(), nullable=True),
        sa.Column('games_position', sa.String(), nullable=True),
        sa.Column('games_rating', sa.Float(), nullable=True),
        sa.Column('games_captain', sa.Boolean(), nullable=True, default=False),
        
        # Statistiques de remplacement
        sa.Column('substitutes_in', sa.Integer(), nullable=True, default=0),
        sa.Column('substitutes_out', sa.Integer(), nullable=True, default=0),
        sa.Column('substitutes_bench', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de tir
        sa.Column('shots_total', sa.Integer(), nullable=True, default=0),
        sa.Column('shots_on', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de but
        sa.Column('goals_total', sa.Integer(), nullable=True, default=0),
        sa.Column('goals_conceded', sa.Integer(), nullable=True, default=0),
        sa.Column('goals_assists', sa.Integer(), nullable=True, default=0),
        sa.Column('goals_saves', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de passe
        sa.Column('passes_total', sa.Integer(), nullable=True, default=0),
        sa.Column('passes_key', sa.Integer(), nullable=True, default=0),
        sa.Column('passes_accuracy', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de tacle
        sa.Column('tackles_total', sa.Integer(), nullable=True, default=0),
        sa.Column('tackles_blocks', sa.Integer(), nullable=True, default=0),
        sa.Column('tackles_interceptions', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de duel
        sa.Column('duels_total', sa.Integer(), nullable=True, default=0),
        sa.Column('duels_won', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de dribble
        sa.Column('dribbles_attempts', sa.Integer(), nullable=True, default=0),
        sa.Column('dribbles_success', sa.Integer(), nullable=True, default=0),
        sa.Column('dribbles_past', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de faute
        sa.Column('fouls_drawn', sa.Integer(), nullable=True, default=0),
        sa.Column('fouls_committed', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de carton
        sa.Column('cards_yellow', sa.Integer(), nullable=True, default=0),
        sa.Column('cards_yellowred', sa.Integer(), nullable=True, default=0),
        sa.Column('cards_red', sa.Integer(), nullable=True, default=0),
        
        # Statistiques de pénalty
        sa.Column('penalty_won', sa.Integer(), nullable=True, default=0),
        sa.Column('penalty_committed', sa.Integer(), nullable=True, default=0),
        sa.Column('penalty_scored', sa.Integer(), nullable=True, default=0),
        sa.Column('penalty_missed', sa.Integer(), nullable=True, default=0),
        sa.Column('penalty_saved', sa.Integer(), nullable=True, default=0),
        
        # Métadonnées
        sa.Column('last_updated', sa.Date(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Création des index pour améliorer les performances
    op.create_index('ix_player_statistics_player_id', 'player_statistics', ['player_id'])
    op.create_index('ix_player_statistics_team_id', 'player_statistics', ['team_id'])
    op.create_index('ix_player_statistics_league_id', 'player_statistics', ['league_id'])
    op.create_index('ix_player_statistics_season', 'player_statistics', ['season'])
    
    # Index composé pour les requêtes fréquentes
    op.create_index(
        'ix_player_statistics_player_season',
        'player_statistics',
        ['player_id', 'season']
    )
    op.create_index(
        'ix_player_statistics_team_season',
        'player_statistics',
        ['team_id', 'season']
    )
    op.create_index(
        'ix_player_statistics_league_season',
        'player_statistics',
        ['league_id', 'season']
    )


def downgrade():
    # Suppression des index
    op.drop_index('ix_player_statistics_league_season', table_name='player_statistics')
    op.drop_index('ix_player_statistics_team_season', table_name='player_statistics')
    op.drop_index('ix_player_statistics_player_season', table_name='player_statistics')
    op.drop_index('ix_player_statistics_season', table_name='player_statistics')
    op.drop_index('ix_player_statistics_league_id', table_name='player_statistics')
    op.drop_index('ix_player_statistics_team_id', table_name='player_statistics')
    op.drop_index('ix_player_statistics_player_id', table_name='player_statistics')
    
    # Suppression de la table
    op.drop_table('player_statistics')