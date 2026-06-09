"""
matching.py — Algorithme de matching mentor ↔ mentoré

Score = 50% compatibilité compétences
      + 30% proximité filière/niveau
      + 20% compatibilité horaires
"""
from models import User, UserCompetence, Disponibilite

# Poids de chaque critère (doivent sommer à 1.0)
POIDS_COMPETENCES  = 0.50
POIDS_FILIERE      = 0.30
POIDS_HORAIRES     = 0.20

# Matrice de proximité entre filières (symétrique)
PROXIMITE_FILIERE = {
    ("GL",     "GL"):     1.0,
    ("GL",     "SI"):     0.7,
    ("GL",     "IM"):     0.6,
    ("GL",     "IA"):     0.5,
    ("GL",     "SE_IoT"): 0.4,
    ("IA",     "IA"):     1.0,
    ("IA",     "IM"):     0.7,
    ("IA",     "SE_IoT"): 0.5,
    ("IA",     "SI"):     0.4,
    ("IM",     "IM"):     1.0,
    ("IM",     "SI"):     0.6,
    ("IM",     "SE_IoT"): 0.5,
    ("SE_IoT", "SE_IoT"): 1.0,
    ("SE_IoT", "SI"):     0.3,
    ("SI",     "SI"):     1.0,
}

def _prox_filiere(f1, f2):
    """Retourne le score de proximité entre deux filières (0.0 – 1.0)."""
    key = (min(f1, f2), max(f1, f2)) if (f1, f2) not in PROXIMITE_FILIERE else (f1, f2)
    return PROXIMITE_FILIERE.get(key, PROXIMITE_FILIERE.get((f2, f1), 0.2))


def _score_competences(mentor: User, mentore: User) -> float:
    """
    Proportion des lacunes du mentoré que le mentor maîtrise.
    Retourne 0.0 si le mentoré n'a aucune lacune déclarée.
    """
    lacunes_ids = {uc.competence_id
                   for uc in mentore.competences
                   if uc.type == "lacune"}
    if not lacunes_ids:
        return 0.0

    maitrise_ids = {uc.competence_id
                    for uc in mentor.competences
                    if uc.type == "maitrise"}
    intersection = lacunes_ids & maitrise_ids
    return len(intersection) / len(lacunes_ids)


def _score_horaires(mentor: User, mentore: User) -> float:
    """
    Proportion des créneaux horaires communs par rapport
    à l'union des créneaux des deux utilisateurs.
    """
    def creneaux(user):
        return {
            (d.jour, d.heure_debut, d.heure_fin)
            for d in user.disponibilites
        }

    c1 = creneaux(mentor)
    c2 = creneaux(mentore)
    union = c1 | c2
    if not union:
        return 0.0
    return len(c1 & c2) / len(union)


def _score_filiere(mentor: User, mentore: User) -> float:
    """Score basé sur la proximité des filières."""
    return _prox_filiere(mentor.filiere, mentore.filiere)


def calculer_score(mentor: User, mentore: User) -> float:
    """
    Calcule le score de compatibilité global entre un mentor
    et un mentoré. Retourne un float entre 0.0 et 100.0.
    """
    s_comp     = _score_competences(mentor, mentore)
    s_horaires = _score_horaires(mentor, mentore)
    s_filiere  = _score_filiere(mentor, mentore)

    score = (
        POIDS_COMPETENCES * s_comp +
        POIDS_FILIERE     * s_filiere +
        POIDS_HORAIRES    * s_horaires
    )
    return round(score * 100, 2)


def proposer_matchs(mentore: User, top_n: int = 10):
    """
    Pour un mentoré donné, retourne les `top_n` meilleurs mentors
    triés par score décroissant.

    Retourne une liste de dict :
        [{"mentor": User, "score": float}, ...]
    """
    # Récupère tous les utilisateurs actifs sauf le mentoré lui-même
    candidats = User.query.filter(
        User.id != mentore.id,
        User.actif == True
    ).all()

    resultats = []
    for candidat in candidats:
        # On vérifie que le candidat a au moins une compétence maîtrisée
        a_maitrise = any(uc.type == "maitrise" for uc in candidat.competences)
        if not a_maitrise:
            continue
        score = calculer_score(candidat, mentore)
        if score > 0:
            resultats.append({"mentor": candidat, "score": score})

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:top_n]
