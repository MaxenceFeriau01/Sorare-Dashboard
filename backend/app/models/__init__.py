"""
Import de tous les modèles pour faciliter leur utilisation
"""
from app.models.player import Player
from app.models.injury import Injury
from app.models.update import Update
from app.models.player_statistics import PlayerStatistics  # ✅ AJOUTER

__all__ = ["Player", "Injury", "Update", "PlayerStatistics"]  # ✅ AJOUTER PlayerStatistics