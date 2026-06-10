# IFRI MentorLink

Plateforme de mise en relation mentor-mentoré pour les étudiants de l'IFRI.

## Stack technique

- **Backend** : Python / Flask + Flask-SocketIO
- **Base de données** : MySQL (via SQLAlchemy + PyMySQL)
- **Auth** : Flask-Login + Flask-Bcrypt
- **Temps réel** : SocketIO (messagerie instantanée)

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/VOTRE_COMPTE/PIL1_2526_XX.git
cd PIL1_2526_XX
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos vraies valeurs
```

### 5. Créer la base de données
```bash
mysql -u root -p < schema.sql
```

### 6. Lancer le serveur
```bash
python app.py
```

Accéder à : http://localhost:5000

## Structure du projet

```
ifri_mentorlink/
├── app.py              # Application Flask principale
├── models.py           # Modèles SQLAlchemy
├── matching.py         # Algorithme de matching
├── schema.sql          # Schéma MySQL
├── requirements.txt
├── .env.example        # Template des variables d'environnement
├── .gitignore
├── routes/
│   ├── auth.py         # Inscription / connexion
│   ├── profil.py       # Dashboard, profil, compétences
│   ├── matching.py     # Suggestions & offres
│   └── messages.py     # Messagerie (SocketIO)
├── templates/          # Templates Jinja2
└── static/             # CSS, JS, images
```

## Algorithme de matching

Le score de compatibilité est calculé ainsi :
- **50%** — Couverture des lacunes du mentoré par les compétences du mentor
- **30%** — Proximité des filières
- **20%** — Compatibilité des disponibilités horaires
