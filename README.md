# 🎓 IFRI MentorLink

Application de mise en relation mentor/mentoré — Projet PIL1 2025-2026

## Structure

```
ifri_mentorlink/
├── app.py              # Point d'entrée Flask
├── models.py           # Modèles SQLAlchemy
├── matching.py         # Algorithme de scoring
├── schema.sql          # Schéma base de données + données initiales
├── requirements.txt
├── .env.example        # Variables d'environnement (à copier en .env)
├── routes/
│   ├── auth.py         # Inscription / Connexion
│   ├── profil.py       # Profil, compétences, offres
│   ├── matching.py     # Suggestions + liste offres
│   └── messages.py     # Messagerie temps réel (SocketIO)
├── templates/          # Pages HTML (Jinja2)
└── static/css/         # style.css
```

## Installation

```bash
# 1. Cloner le repo
git clone https://github.com/votre-groupe/PIL1_2526_XX.git
cd PIL1_2526_XX

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Base de données MySQL
mysql -u root -p < schema.sql
# (crée la base, les tables et les compétences de départ)

# 5. Variables d'environnement
cp .env.example .env
# Éditer .env : mettre votre mot de passe MySQL

# 6. Lancer
python app.py
# → http://localhost:5000
```

## Variables d'environnement (.env)

```
SECRET_KEY=une-chaine-aleatoire-longue
DATABASE_URL=mysql://root:VOTRE_MDP@localhost/ifri_mentorlink
```

## Fonctionnalités

| Module | Routes |
|--------|--------|
| Auth | `/inscription`, `/connexion`, `/deconnexion` |
| Profil | `/dashboard`, `/profil`, `/offre/nouvelle` |
| Matching | `/matching`, `/offres` |
| Messages | `/messages`, `/messages/<id>` |
