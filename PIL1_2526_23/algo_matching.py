"""
algo_matching.py — Algorithme de matching mentor ↔ mentoré
"""
from models import User

POIDS_COMPETENCES  = 0.50
POIDS_FILIERE      = 0.30
POIDS_HORAIRES     = 0.20

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
    key = (f1, f2) if (f1, f2) in PROXIMITE_FILIERE else (f2, f1)
    return PROXIMITE_FILIERE.get(key, 0.2)

def _score_competences(mentor, mentore):
    lacunes_ids = {uc.competence_id for uc in mentore.competences if uc.type == "lacune"}
    if not lacunes_ids:
        return 0.0
    maitrise_ids = {uc.competence_id for uc in mentor.competences if uc.type == "maitrise"}
    return len(lacunes_ids & maitrise_ids) / len(lacunes_ids)

def _score_horaires(mentor, mentore):
    def creneaux(user):
        return {(d.jour, d.heure_debut, d.heure_fin) for d in user.disponibilites}
    c1, c2 = creneaux(mentor), creneaux(mentore)
    union = c1 | c2
    if not union:
        return 0.0
    return len(c1 & c2) / len(union)

def _score_filiere(mentor, mentore):
    return _prox_filiere(mentor.filiere, mentore.filiere)

def calculer_score(mentor, mentore):
    score = (
        POIDS_COMPETENCES * _score_competences(mentor, mentore) +
        POIDS_FILIERE     * _score_filiere(mentor, mentore) +
        POIDS_HORAIRES    * _score_horaires(mentor, mentore)
    )
    return round(score * 100, 2)

def proposer_matchs(mentore, top_n=10):
    candidats = User.query.filter(User.id != mentore.id, User.actif == True).all()
    resultats = []
    for candidat in candidats:
        if any(uc.type == "maitrise" for uc in candidat.competences):
            score = calculer_score(candidat, mentore)
            if score > 0:
                resultats.append({"mentor": candidat, "score": score})
    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:top_n]
