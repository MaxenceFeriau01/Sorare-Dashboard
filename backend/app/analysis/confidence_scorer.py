"""
Analyseur de texte avec calcul de confiance pour détecter les blessures
"""
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger

from .keywords import (
    INJURY_KEYWORDS,
    AVAILABILITY_KEYWORDS,
    CONTEXT_PATTERNS,
    SOURCE_RELIABILITY,
    CONFIDENCE_THRESHOLDS,
)


class InjuryAnalyzer:
    """
    Analyse un texte pour détecter les blessures et calculer un score de confiance
    """
    
    def __init__(self):
        self.injury_keywords = INJURY_KEYWORDS
        self.availability_keywords = AVAILABILITY_KEYWORDS
        self.context_patterns = CONTEXT_PATTERNS
        self.thresholds = CONFIDENCE_THRESHOLDS
    
    def analyze_text(
        self,
        text: str,
        player_name: str,
        source: str = "unknown",
        source_type: str = "website"
    ) -> Dict:
        """
        Analyse un texte pour détecter une blessure
        
        Args:
            text: Le texte à analyser
            player_name: Le nom du joueur
            source: La source de l'information
            source_type: Type de source (website, twitter, etc.)
            
        Returns:
            Dict avec les résultats de l'analyse
        """
        text_lower = text.lower()
        player_name_lower = player_name.lower()
        
        # Vérifier que le joueur est mentionné
        if player_name_lower not in text_lower:
            return {
                "is_injury": False,
                "confidence": 0.0,
                "reason": "Player not mentioned in text",
            }
        
        # 1. Calculer le score de blessure
        injury_score = self._calculate_injury_score(text_lower)
        
        # 2. Détecter la gravité
        severity = self._detect_severity(text_lower)
        
        # 3. Extraire la durée d'absence
        duration_days = self._extract_duration(text_lower)
        
        # 4. Détecter le type de blessure
        injury_type = self._detect_injury_type(text_lower)
        
        # 5. Vérifier les négations
        has_negation = self._check_negation(text_lower, player_name_lower)
        
        # 6. Vérifier les confirmations
        is_confirmed = self._check_confirmation(text_lower)
        
        # 7. Calculer le score de fiabilité de la source
        source_reliability = self._get_source_reliability(source, source_type)
        
        # 8. Calculer le score final de confiance
        final_confidence = self._calculate_final_confidence(
            injury_score=injury_score,
            has_negation=has_negation,
            is_confirmed=is_confirmed,
            source_reliability=source_reliability,
        )
        
        # 9. Déterminer si c'est une blessure
        is_injury = final_confidence >= self.thresholds["blessure_probable"]
        
        # 10. Calculer la disponibilité
        availability = self._calculate_availability(text_lower, is_injury, final_confidence)
        
        return {
            "is_injury": is_injury,
            "confidence": round(final_confidence, 2),
            "injury_score": round(injury_score, 2),
            "severity": severity,
            "injury_type": injury_type,
            "duration_days": duration_days,
            "has_negation": has_negation,
            "is_confirmed": is_confirmed,
            "source_reliability": round(source_reliability, 2),
            "availability_percentage": availability,
            "interpretation": self._get_interpretation(final_confidence, is_injury),
            "matched_keywords": self._get_matched_keywords(text_lower),
        }
    
    def _calculate_injury_score(self, text: str) -> float:
        """Calcule le score de blessure basé sur les mots-clés"""
        score = 0.0
        
        for category, data in self.injury_keywords.items():
            for keyword in data["keywords"]:
                if keyword in text:
                    score += data["weight"]
        
        # Normaliser le score entre 0 et 1
        return min(score / 10.0, 1.0)
    
    def _detect_severity(self, text: str) -> Optional[str]:
        """Détecte la gravité de la blessure"""
        severity_keywords = self.injury_keywords.get("gravite", {}).get("keywords", [])
        
        for keyword in severity_keywords:
            if keyword in text:
                if any(word in keyword for word in ["grave", "rupture", "fracture", "déchirure", "severe", "torn"]):
                    return "Severe"
                elif any(word in keyword for word in ["sérieux", "serious", "plusieurs semaines"]):
                    return "Moderate"
        
        return "Minor"
    
    def _detect_injury_type(self, text: str) -> Optional[str]:
        """Détecte le type de blessure"""
        type_keywords = self.injury_keywords.get("type_blessure", {}).get("keywords", [])
        
        detected_types = []
        for keyword in type_keywords:
            if keyword in text:
                detected_types.append(keyword)
        
        return detected_types[0].capitalize() if detected_types else None
    
    def _extract_duration(self, text: str) -> Optional[int]:
        """Extrait la durée d'absence en jours"""
        patterns = self.context_patterns["duree"]["patterns"]
        multipliers = self.context_patterns["duree"]["multipliers"]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        number = int(match[0])
                        unit = match[1]
                        
                        # Trouver le multiplicateur
                        for key, mult in multipliers.items():
                            if key in unit:
                                return number * mult
        
        return None
    
    def _check_negation(self, text: str, player_name: str) -> bool:
        """Vérifie si il y a une négation (pas blessé)"""
        negation_words = self.context_patterns["negation"]["keywords"]
        
        # Extraire le contexte autour du nom du joueur
        player_index = text.find(player_name)
        if player_index == -1:
            return False
        
        # Contexte de 100 caractères avant et après
        context_start = max(0, player_index - 100)
        context_end = min(len(text), player_index + len(player_name) + 100)
        context = text[context_start:context_end]
        
        # Vérifier les négations
        for neg_word in negation_words:
            if neg_word in context:
                return True
        
        return False
    
    def _check_confirmation(self, text: str) -> bool:
        """Vérifie si l'information est confirmée"""
        confirmation_words = self.context_patterns["confirmation"]["keywords"]
        
        for word in confirmation_words:
            if word in text:
                return True
        
        return False
    
    def _get_source_reliability(self, source: str, source_type: str) -> float:
        """Calcule la fiabilité de la source"""
        if source_type == "twitter":
            accounts = SOURCE_RELIABILITY["twitter"]
            
            # Vérifier si c'est un compte vérifié connu
            for account, reliability in accounts["verified_accounts"].items():
                if account.lower() in source.lower():
                    return reliability
            
            # Par défaut : compte inconnu
            return accounts["unknown"]
        
        elif source_type == "website":
            websites = SOURCE_RELIABILITY["websites"]
            
            for domain, reliability in websites.items():
                if domain in source.lower():
                    return reliability
            
            return 0.6  # Fiabilité moyenne par défaut
        
        return 0.5
    
    def _calculate_final_confidence(
        self,
        injury_score: float,
        has_negation: bool,
        is_confirmed: bool,
        source_reliability: float,
    ) -> float:
        """Calcule le score final de confiance"""
        
        # Base : score de blessure
        confidence = injury_score
        
        # Ajuster avec la négation
        if has_negation:
            confidence *= 0.2  # Réduire drastiquement si négation
        
        # Augmenter si confirmé
        if is_confirmed:
            confidence *= 1.3
        
        # Pondérer avec la fiabilité de la source
        confidence *= source_reliability
        
        # Normaliser entre 0 et 1
        return min(confidence, 1.0)
    
    def _calculate_availability(self, text: str, is_injury: bool, confidence: float) -> int:
        """Calcule le pourcentage de disponibilité (0-100)"""
        
        if not is_injury:
            # Chercher des indices de disponibilité
            for category, data in self.availability_keywords.items():
                for keyword in data["keywords"]:
                    if keyword in text:
                        return int(data["confidence"] * 100)
            
            return 90  # Par défaut : probablement disponible
        
        else:
            # Blessé : faible disponibilité
            if confidence >= 0.8:
                return 10  # Blessure confirmée
            elif confidence >= 0.5:
                return 30  # Blessure probable
            else:
                return 50  # Incertain
    
    def _get_interpretation(self, confidence: float, is_injury: bool) -> str:
        """Génère une interprétation humaine du résultat"""
        if not is_injury:
            return "Aucune blessure détectée"
        
        if confidence >= self.thresholds["blessure_confirmee"]:
            return "Blessure confirmée avec haute confiance"
        elif confidence >= self.thresholds["blessure_probable"]:
            return "Blessure probable, à surveiller"
        elif confidence >= self.thresholds["blessure_douteuse"]:
            return "Mention de blessure douteuse"
        else:
            return "Information non fiable"
    
    def _get_matched_keywords(self, text: str) -> List[str]:
        """Retourne la liste des mots-clés matchés"""
        matched = []
        
        for category, data in self.injury_keywords.items():
            for keyword in data["keywords"]:
                if keyword in text:
                    matched.append(keyword)
        
        return matched[:10]  # Limiter à 10 pour ne pas surcharger


# Instance globale
injury_analyzer = InjuryAnalyzer()