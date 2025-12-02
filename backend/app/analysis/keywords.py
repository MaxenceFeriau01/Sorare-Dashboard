"""
Définitions des mots-clés et constantes de confiance pour l'analyse des blessures.
"""
from typing import Dict, List, Any

# ======================================================================
# 1. Mots-clés de Blessure (INJURY_KEYWORDS)
# ======================================================================

INJURY_KEYWORDS: Dict[str, Dict[str, Any]] = {
    "blessure_generale": {
        "keywords": [
            "blessure", "injury", "injured", "douleur", "pain", 
            "gêne", "knock", "problème physique", "physical issue", 
            "problème musculaire", "muscle issue", "malade", "illness",
            "incertain", "doubt", "incertitude", "absent", "absent for",
            "out", "forfait", "ruled out", "écarté", "sidelined",
            "absence", "inaptitude", "ko"
        ],
        "weight": 1.5 
    },
    "gravite": {
        "keywords": [
            "grave", "severe", "sérieux", "serious", "légère", "minor", 
            "longue durée", "long-term", "rechute", "relapse", 
            "aggravation", "worsening", "touché", "rupture", "déchirure", 
            "déchiré", "torn", "fracture", "broken", "opéré", "surgery",
            "plusieurs semaines", "3 mois", "ligaments" # Ajouté pour la gravité
        ],
        "weight": 2.5 
    },
    "type_blessure": {
        "keywords": [
            "cheville", "ankle", "genou", "knee", "cuisse", "thigh", 
            "ischio", "hamstring", "mollet", "calf", "adducteur", "adductor",
            "ligament", "ligamentaire", "menisque", "ménisque", "tendon", 
            "tendinite", "commotion", "concussion", "épaule", "shoulder",
            "dos", "back", "poignet", "wrist"
        ],
        "weight": 1.8 
    },
    "termes_absence": {
        "keywords": [
            "miss", "manquer", "rater", "return date", "date de retour", 
            "prochain match", "next match", "absent contre", "miss against"
        ],
        "weight": 1.2
    }
}

# ======================================================================
# 2. Mots-clés de Disponibilité (AVAILABILITY_KEYWORDS)
# ======================================================================

AVAILABILITY_KEYWORDS: Dict[str, Dict[str, Any]] = {
    "titularisation_forte": {
        "keywords": [
            "titulaire", "starts", "starting", "lineup", 
            "composition", "XI de départ", "first XI", "débutera",
            "aligné", "alignement", "starter", "squad", "dans le groupe",
            "starting eleven", "team sheet", "on the field"
        ],
        "confidence": 0.95 
    },
    "titularisation_moyenne": {
        "keywords": [
            "bench", "remplaçant", "substitut", "sur le banc", 
            "disponible", "available", "present", "présent", 
            "convoc", "convoqué", "in the squad", "en forme",
            "on the bench", "sub", "reserves"
        ],
        "confidence": 0.70 
    },
    "entrainement": {
        "keywords": [
            "entrainement", "training", "reprise", "session", 
            "récupération", "full training", "entraînement complet",
            "practiced", "s'entraîne", "with the team"
        ],
        "confidence": 0.55 
    },
    "recherche_composition": {
        "keywords": [
            "lineup", "titulaire", "composition", "start", 
            "bench", "remplaçant"
        ],
        "confidence": 0.0
    }
}

# ======================================================================
# 3. Modèles de Contexte (CONTEXT_PATTERNS)
# ======================================================================

CONTEXT_PATTERNS: Dict[str, Dict[str, Any]] = {
    "phrases_cles": {
        "keywords": [
            "likely to miss", "probable d'être absent", "out for", "absent pour", 
            "ne jouera pas", "will not play", "ruled out", "écarté",
            "incertain pour", "doubtful for", "absent contre", "missed training"
        ],
    },
    
    "negation": {
        "keywords": ["pas blessé", "not injured", "il va bien", "sera titulaire", "no injury", "non blessé", "fit to play", "aucune blessure"],
    },
    
    "confirmation": {
        "keywords": ["confirmé par", "officialisé par", "selon arteta", "selon guardiola", "confirms", "official statement", "club annonce", "mikel arteta", "ten hag", "klopp", "statement from club"],
    },
    
    "duree": {
        "patterns": [
            # Pattern pour extraire (Nombre) (Unité: jours/semaines/mois)
            r'(\d+)\s+(jour|jours|semaine|semaines|mois)', 
        ],
        "multipliers": {
            "jour": 1, "jours": 1,
            "semaine": 7, "semaines": 7,
            "mois": 30,
        }
    }
}

# ======================================================================
# 4. Seuils et Fiabilité de la Source
# ======================================================================

CONFIDENCE_THRESHOLDS: Dict[str, float] = {
    "blessure_confirmee": 0.85,
    "blessure_probable": 0.50,
    "blessure_douteuse": 0.30,
}

SOURCE_RELIABILITY: Dict[str, Dict[str, Any]] = {
    "twitter": {
        "verified_accounts": {
            "fabrizioromano": 0.90,
            "ornstein": 0.85,
            "davidornstein": 0.85,
            "mohamedbouhafsi": 0.80,
            "officialarsenal": 0.99, # Exemple de compte club
            "unknown": 0.30, 
        },
        "unknown": 0.30
    },
    "websites": {
        "lequipe.fr": 0.80,
        "bbc.com": 0.85,
        "skysports.com": 0.75,
        "lfp.fr": 0.95,
    }
}