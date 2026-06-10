# IFRI MentorLink — PIL1_2526_23

Plateforme de mise en relation mentor-mentoré pour les étudiants de l'IFRI.

## Stack
- **Backend** : Python / Flask + Flask-SocketIO
- **DB** : MySQL (SQLAlchemy + PyMySQL)
- **Auth** : Flask-Login + Flask-Bcrypt
- **Temps réel** : SocketIO

## Installation rapide

```bash
# 1. Cloner
git clone https://github.com/tresornelky00-cloud/PIL1_2526_23.git
cd PIL1_2526_23

# 2. Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Dépendances
pip install -r requirements.txt

# 4. Config
cp .env.example .env
# Editer .env avec vos valeurs

# 5. Base de données
mysql -u root -p < schema.sql

# 6. Lancer
python app.py
```

Accéder à : http://localhost:5000
