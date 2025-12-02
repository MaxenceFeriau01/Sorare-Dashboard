"""
Schemas Pydantic pour la validation des données de blessures
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InjuryBase(BaseModel):
    """Schema de base pour une blessure"""
    player_id: int
    injury_type: Optional[str] = None
    injury_description: Optional[str] = None
    severity: Optional[str] = None
    injury_date: Optional[datetime] = None
    expected_return_date: Optional[datetime] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class InjuryCreate(InjuryBase):
    """Schema pour créer une blessure"""
    pass


class InjuryUpdate(BaseModel):
    """Schema pour mettre à jour une blessure"""
    injury_type: Optional[str] = None
    injury_description: Optional[str] = None
    severity: Optional[str] = None
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class InjuryResponse(InjuryBase):
    """Schema de réponse pour une blessure"""
    id: int
    actual_return_date: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InjuryListResponse(BaseModel):
    """Schema pour une liste de blessures"""
    total: int
    injuries: list[InjuryResponse]