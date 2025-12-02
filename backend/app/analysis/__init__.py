"""
Module d'analyse intelligente pour la détection de blessures
"""
from .confidence_scorer import injury_analyzer
from .keywords import (
    INJURY_KEYWORDS,
    AVAILABILITY_KEYWORDS,
    CONTEXT_PATTERNS,
    SOURCE_RELIABILITY,
    CONFIDENCE_THRESHOLDS,
)

__all__ = [
    "injury_analyzer",
    "INJURY_KEYWORDS",
    "AVAILABILITY_KEYWORDS",
    "CONTEXT_PATTERNS",
    "SOURCE_RELIABILITY",
    "CONFIDENCE_THRESHOLDS",
]