"""
Filtre intelligent pour détecter les vraies blessures
Version 2 - Priorité à la RAISON sur le TYPE
"""
from typing import Optional
from loguru import logger


class InjuryFilter:
    """
    Filtre pour distinguer les vraies blessures des absences non médicales
    
    L'API-Football retourne TOUTES les absences dans /injuries:
    - Type "Missing Fixture" = Le joueur ne joue pas (peut être blessé OU suspendu OU au repos)
    - Type "Questionable" = Information pas sûre
    
    La RAISON (reason) est la vraie information à analyser !
    """
    
    # Mots-clés indiquant une VRAIE blessure
    REAL_INJURY_KEYWORDS = [
        # Blessures générales
        'injury', 'injured', 'blessure', 'blessé',
        
        # Types de blessures
        'fracture', 'broken', 'torn', 'rupture', 'ruptured',
        'sprain', 'sprained', 'strain', 'strained',
        'dislocation', 'dislocated', 'concussion',
        
        # Parties du corps
        'ankle', 'knee', 'hamstring', 'groin', 'thigh', 'calf',
        'achilles', 'shoulder', 'hip', 'back', 'neck',
        'foot', 'toe', 'finger', 'wrist', 'elbow',
        'muscle', 'ligament', 'tendon', 'cartilage',
        
        # Problèmes médicaux
        'surgery', 'operation', 'recovery', 'rehabilitation',
        'illness', 'sick', 'covid', 'virus', 'infection',
        'pain', 'ache', 'sore', 'inflammation',
        
        # Termes médicaux
        'acl', 'mcl', 'pcl', 'meniscus', 'patella',
        'fibula', 'tibia', 'femur', 'metatarsal',
        'adductor', 'abductor', 'quadriceps', 'gastrocnemius'
    ]
    
    # Mots-clés indiquant une FAUSSE blessure (absence non médicale)
    FAKE_INJURY_KEYWORDS = [
        # Suspensions
        'suspended', 'suspension', 'ban', 'banned',
        'red card', 'yellow card', 'sent off',
        
        # Repos / Rotation
        'rest', 'rested', 'rotation', 'rotated',
        'tactical', 'coach decision', 'technical decision',
        'not in squad', 'left out', 'dropped',
        
        # Incertitudes (pas une vraie blessure confirmée)
        'doubtful', 'doubt', 'uncertain', 'questionable',
        'fitness test', 'late fitness test',
        
        # Autres raisons
        'personal', 'family', 'compassionate',
        'international duty', 'with national team',
        'lack of fitness', 'fitness issues'
    ]
    
    @classmethod
    def is_real_injury(cls, injury_type: Optional[str], injury_reason: Optional[str]) -> bool:
        """
        Détermine si une blessure est réelle ou non
        
        NOUVELLE LOGIQUE (VERSION 2):
        1. Vérifier la RAISON en priorité (c'est l'info la plus précise)
        2. Si la raison contient un mot-clé de vraie blessure → VRAI
        3. Si la raison contient un mot-clé de fausse blessure → FAUX
        4. Ensuite seulement vérifier le TYPE
        5. Par défaut → FAUX (principe de précaution)
        
        Args:
            injury_type: Type de l'absence (ex: "Missing Fixture", "Questionable")
            injury_reason: Raison détaillée (ex: "Ankle Injury", "Suspended")
            
        Returns:
            bool: True si vraie blessure, False sinon
        """
        injury_type_lower = (injury_type or '').lower()
        injury_reason_lower = (injury_reason or '').lower()
        
        # ÉTAPE 1: Vérifier d'abord la RAISON pour les vraies blessures
        # Si la raison mentionne une vraie blessure → c'est une vraie blessure
        if injury_reason_lower:
            for keyword in cls.REAL_INJURY_KEYWORDS:
                if keyword in injury_reason_lower:
                    logger.debug(
                        f"✅ Vraie blessure détectée (raison: '{keyword}'): "
                        f"{injury_type} {injury_reason}"
                    )
                    return True
        
        # ÉTAPE 2: Vérifier la RAISON pour les fausses blessures
        # Si la raison indique une suspension/repos → fausse blessure
        if injury_reason_lower:
            for keyword in cls.FAKE_INJURY_KEYWORDS:
                if keyword in injury_reason_lower:
                    logger.debug(
                        f"❌ Fausse blessure (raison: '{keyword}'): "
                        f"{injury_type} {injury_reason}"
                    )
                    return False
        
        # ÉTAPE 3: Vérifier le TYPE seulement si la raison n'a rien donné
        # Si le type contient "questionable" mais pas d'info dans la raison → fausse blessure
        if injury_type_lower:
            for keyword in cls.FAKE_INJURY_KEYWORDS:
                if keyword in injury_type_lower:
                    # Exception: si "questionable" mais la raison est vide, on ignore
                    if keyword == 'questionable' and not injury_reason_lower:
                        logger.debug(
                            f"⚠️ Type 'questionable' sans raison précise: "
                            f"{injury_type} - considéré comme faux"
                        )
                        return False
        
        # ÉTAPE 4: Si le type est "Missing Fixture" mais aucune info précise
        # → Principe de précaution: on considère que ce n'est pas une blessure
        if 'missing fixture' in injury_type_lower and not injury_reason_lower:
            logger.debug(
                f"⚠️ 'Missing Fixture' sans raison précise - considéré comme absence non médicale"
            )
            return False
        
        # ÉTAPE 5: Par défaut, si aucun mot-clé détecté
        # → Principe de précaution: fausse blessure
        logger.debug(
            f"⚠️ Aucun mot-clé détecté, considéré comme fausse blessure par défaut: "
            f"{injury_type} {injury_reason}"
        )
        return False
    
    @classmethod
    def get_injury_confidence(cls, injury_type: Optional[str], injury_reason: Optional[str]) -> float:
        """
        Calcule un score de confiance pour la détection de blessure
        
        Args:
            injury_type: Type de l'absence
            injury_reason: Raison détaillée
            
        Returns:
            float: Score de confiance entre 0 et 1
                   1.0 = Très confiant que c'est une vraie blessure
                   0.0 = Très confiant que c'est une fausse blessure
        """
        injury_type_lower = (injury_type or '').lower()
        injury_reason_lower = (injury_reason or '').lower()
        
        confidence = 0.5  # Score neutre de base
        
        # Bonus pour les mots-clés de vraie blessure dans la raison
        if injury_reason_lower:
            real_matches = sum(1 for kw in cls.REAL_INJURY_KEYWORDS if kw in injury_reason_lower)
            if real_matches > 0:
                confidence += min(real_matches * 0.2, 0.5)  # Max +0.5
        
        # Malus pour les mots-clés de fausse blessure dans la raison
        if injury_reason_lower:
            fake_matches = sum(1 for kw in cls.FAKE_INJURY_KEYWORDS if kw in injury_reason_lower)
            if fake_matches > 0:
                confidence -= min(fake_matches * 0.3, 0.5)  # Max -0.5
        
        # Limiter entre 0 et 1
        return max(0.0, min(1.0, confidence))
    
    @classmethod
    def get_injury_severity(cls, injury_reason: Optional[str]) -> str:
        """
        Estime la gravité de la blessure
        
        Args:
            injury_reason: Raison de la blessure
            
        Returns:
            str: "Minor", "Moderate", "Severe", ou "Unknown"
        """
        if not injury_reason:
            return "Unknown"
        
        injury_reason_lower = injury_reason.lower()
        
        # Blessures graves
        severe_keywords = ['fracture', 'broken', 'torn', 'rupture', 'surgery', 'acl', 'mcl']
        if any(kw in injury_reason_lower for kw in severe_keywords):
            return "Severe"
        
        # Blessures modérées
        moderate_keywords = ['sprain', 'strain', 'inflammation', 'ligament', 'meniscus']
        if any(kw in injury_reason_lower for kw in moderate_keywords):
            return "Moderate"
        
        # Blessures mineures
        minor_keywords = ['pain', 'ache', 'sore', 'fatigue', 'minor']
        if any(kw in injury_reason_lower for kw in minor_keywords):
            return "Minor"
        
        return "Unknown"