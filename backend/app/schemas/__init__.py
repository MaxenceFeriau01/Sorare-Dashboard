"""
Import de tous les schemas pour faciliter leur utilisation
"""
from app.schemas.player import (
    PlayerBase,
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerListResponse
)
from app.schemas.injury import (
    InjuryBase,
    InjuryCreate,
    InjuryUpdate,
    InjuryResponse,
    InjuryListResponse
)

__all__ = [
    "PlayerBase",
    "PlayerCreate",
    "PlayerUpdate",
    "PlayerResponse",
    "PlayerListResponse",
    "InjuryBase",
    "InjuryCreate",
    "InjuryUpdate",
    "InjuryResponse",
    "InjuryListResponse",
]