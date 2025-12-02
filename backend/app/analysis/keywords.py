"""
Configuration des mots-clés et patterns pour la détection de blessures et de statuts
"""

# ============================================
# MOTS-CLÉS BLESSURES
# ============================================

INJURY_KEYWORDS = {
    "blessure": {
        "keywords": [
            "blessé", "blessure", "forfait", "absent", "indisponible",
            "touché", "victime", "souffre", "douleur", "gêne",
            "ko", "out", "injured", "injury", "hurt", "pain",
            "problema", "lesión", "lesionado"
        ],
        "weight": 2.0,  # Poids élevé = forte indication
    },
    
    "gravite": {
        "keywords": [
            "grave", "sérieux", "longue durée", "plusieurs semaines", "plusieurs mois",
            "rupture", "fracture", "déchirure", "entorse",
            "opération", "chirurgie", "intervention",
            "severe", "serious", "surgery", "torn", "broken"
        ],
        "weight": 1.5,
    },
    
    "type_blessure": {
        "keywords": [
            # Musculaires
            "musculaire", "ischio", "quadriceps", "mollet", "adducteurs",
            "hamstring", "calf", "thigh", "groin",
            
            # Articulations
            "genou", "cheville", "épaule", "dos", "hanche",
            "knee", "ankle", "shoulder", "back", "hip",
            
            # Ligaments
            "ligament", "croisé", "LCA", "LCP", "ACL", "PCL",
            
            # Autres
            "commotion", "côtes", "concussion", "ribs"
        ],
        "weight": 1.2,
    },
    
    "retour": {
        "keywords": [
            "retour prévu", "absent", "semaines", "mois", "jours",
            "forfait pour", "indisponible pendant",
            "expected back", "out for", "sidelined",
            "de baja", "recuperación"
        ],
        "weight": 1.0,
    },
}

# ============================================
# MOTS-CLÉS DISPONIBILITÉ
# ============================================

AVAILABILITY_KEYWORDS = {
    "incertain": {
        "keywords": [
            "incertain", "doute", "évaluation", "tests", "examens",
            "décision", "incertitude", "attente",
            "doubtful", "questionable", "day-to-day", "game-time decision",
            "duda", "evaluación"
        ],
        "confidence": 0.5,  # 50% de confiance
    },
    
    "probablement_absent": {
        "keywords": [
            "très incertain", "peu de chances", "probablement forfait",
            "unlikely", "probably out", "not expected",
            "poco probable"
        ],
        "confidence": 0.2,  # 20% de chances de jouer
    },
    
    "retour_imminent": {
        "keywords": [
            "de retour", "rétabli", "apte", "groupe", "reprise",
            "retour à l'entraînement", "back in training",
            "returned", "fit", "recovered", "available",
            "recuperado", "disponible"
        ],
        "confidence": 0.8,  # 80% de chances de jouer
    },
    
    "titulaire": {
        "keywords": [
            "titulaire", "alignement", "composition", "starting",
            "XI de départ", "onze", "lineup", "starting eleven",
            "titular", "once inicial"
        ],
        "confidence": 0.9,  # 90% de chances de jouer
    },
}

# ============================================
# PATTERNS DE CONTEXTE
# ============================================

CONTEXT_PATTERNS = {
    "duree": {
        # Patterns pour extraire la durée d'absence
        "patterns": [
            r"(\d+)\s+(jour|jours|day|days|día|días)",
            r"(\d+)\s+(semaine|semaines|week|weeks|semana|semanas)",
            r"(\d+)\s+(mois|month|months|mes|meses)",
            r"plusieurs\s+(semaines|mois)",
            r"quelques\s+(jours|semaines)",
        ],
        "multipliers": {
            "jour": 1,
            "semaine": 7,
            "mois": 30,
        }
    },
    
    "negation": {
        # Mots qui inversent le sens
        "keywords": [
            "pas", "non", "aucun", "sans", "ne", "ni",
            "not", "no", "neither", "nor", "without",
            "sin", "ningún"
        ],
        "weight": -1.0,  # Inverse le score
    },
    
    "confirmation": {
        # Mots qui confirment l'information
        "keywords": [
            "confirmé", "officiel", "annoncé", "déclaré",
            "confirmed", "official", "announced", "stated",
            "confirmado", "oficial"
        ],
        "weight": 1.5,  # Augmente la confiance
    },
}

# ============================================
# SOURCES ET FIABILITÉ
# ============================================

SOURCE_RELIABILITY = {
    # Score de fiabilité par source (0-1)
    "twitter": {
        "verified_accounts": {
            "Squawka": 0.9,
            "FabrizioRomano": 0.95,
            "lequipe": 0.95,
            "RMCsport": 0.9,
            "footmercato": 0.85,
            "OptaJoe": 0.9,
            "WhoScored": 0.85,
        },
        "club_official": 1.0,  # Comptes officiels des clubs
        "journalist": 0.8,      # Journalistes vérifiés
        "fan_account": 0.3,     # Comptes de fans
        "unknown": 0.2,         # Comptes inconnus
    },
    
    "websites": {
        "lequipe.fr": 0.95,
        "transfermarkt.com": 0.9,
        "footmercato.net": 0.85,
        "goal.com": 0.8,
        "eurosport.fr": 0.9,
        "sofoot.com": 0.85,
        "rmcsport.bfmtv.com": 0.9,
    }
}

# ============================================
# SEUILS DE CONFIANCE
# ============================================

CONFIDENCE_THRESHOLDS = {
    "blessure_confirmee": 0.75,      # 75%+ = blessure confirmée
    "blessure_probable": 0.50,       # 50-75% = blessure probable
    "blessure_douteuse": 0.30,       # 30-50% = à surveiller
    "info_non_fiable": 0.30,         # <30% = ignorer
    
    "disponibilite_confirmee": 0.80, # 80%+ = disponible
    "disponibilite_probable": 0.60,  # 60-80% = probablement dispo
    "incertain": 0.40,               # 40-60% = incertain
    "indisponible": 0.20,            # <40% = probablement absent
}

# ============================================
# CLUBS À SURVEILLER (optionnel)
# ============================================

PRIORITY_CLUBS = [
    "Real Madrid", "Manchester City", "PSG", "Bayern Munich",
    "Liverpool", "Barcelona", "Arsenal", "Manchester United",
    # Ajoute les clubs de tes joueurs ici
]