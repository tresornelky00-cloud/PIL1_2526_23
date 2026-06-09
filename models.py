"""
models.py — Modèles de la base de données (SQLAlchemy)
"""
from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Table pivot users ↔ competences ──────────────────────────
class UserCompetence(db.Model):
    __tablename__ = "user_competences"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey("competences.id"), nullable=False)
    type          = db.Column(db.Enum("maitrise", "lacune"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "competence_id", "type", name="uq_user_comp_type"),
    )


# ── User ─────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id               = db.Column(db.Integer, primary_key=True)
    nom              = db.Column(db.String(100), nullable=False)
    prenom           = db.Column(db.String(100), nullable=False)
    email            = db.Column(db.String(255), unique=True, nullable=False)
    telephone        = db.Column(db.String(20),  unique=True, nullable=False)
    mot_de_passe     = db.Column(db.String(255), nullable=False)
    photo_profil     = db.Column(db.String(500), default=None)
    filiere          = db.Column(db.Enum("GL","IA","IM","SE_IoT","SI"), nullable=False)
    niveau           = db.Column(db.Enum("L1","L2","L3","M1","M2"),   nullable=False)
    bio              = db.Column(db.Text, default=None)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    actif            = db.Column(db.Boolean, default=True)

    # Relations
    competences   = db.relationship("UserCompetence", backref="user",   lazy="dynamic")
    disponibilites = db.relationship("Disponibilite",  backref="user",   lazy="dynamic")
    offres        = db.relationship("OffreMentorat",   backref="auteur", lazy="dynamic")

    def maitrisees(self):
        """Retourne les compétences maîtrisées de l'utilisateur."""
        return (
            db.session.query(Competence)
            .join(UserCompetence)
            .filter(UserCompetence.user_id == self.id,
                    UserCompetence.type == "maitrise")
            .all()
        )

    def lacunes(self):
        """Retourne les lacunes de l'utilisateur."""
        return (
            db.session.query(Competence)
            .join(UserCompetence)
            .filter(UserCompetence.user_id == self.id,
                    UserCompetence.type == "lacune")
            .all()
        )


# ── Compétence ───────────────────────────────────────────────
class Competence(db.Model):
    __tablename__ = "competences"
    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(100), unique=True, nullable=False)
    categorie = db.Column(db.String(50), default="Général")


# ── Disponibilite ────────────────────────────────────────────
class Disponibilite(db.Model):
    __tablename__ = "disponibilites"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jour        = db.Column(db.Enum("Lundi","Mardi","Mercredi","Jeudi",
                                    "Vendredi","Samedi","Dimanche"), nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin   = db.Column(db.Time, nullable=False)


# ── OffreMentorat ────────────────────────────────────────────
class OffreMentorat(db.Model):
    __tablename__ = "offres_mentorat"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"),       nullable=False)
    type_offre    = db.Column(db.Enum("offre","demande"),                   nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey("competences.id"), nullable=False)
    format        = db.Column(db.Enum("presentiel","en_ligne","les_deux"), default="les_deux")
    description   = db.Column(db.Text, default=None)
    active        = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    competence = db.relationship("Competence", backref="offres")


# ── Match ────────────────────────────────────────────────────
class Match(db.Model):
    __tablename__ = "matchs"
    id          = db.Column(db.Integer, primary_key=True)
    mentor_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentore_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score       = db.Column(db.Numeric(5, 2), nullable=False)
    statut      = db.Column(db.Enum("propose","accepte","refuse","termine"), default="propose")
    date_match  = db.Column(db.DateTime, default=datetime.utcnow)

    mentor  = db.relationship("User", foreign_keys=[mentor_id],  backref="comme_mentor")
    mentore = db.relationship("User", foreign_keys=[mentore_id], backref="comme_mentore")

    __table_args__ = (
        db.UniqueConstraint("mentor_id", "mentore_id", name="uq_match"),
    )


# ── Conversation ─────────────────────────────────────────────
class Conversation(db.Model):
    __tablename__ = "conversations"
    id            = db.Column(db.Integer, primary_key=True)
    user1_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user2_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    user1    = db.relationship("User", foreign_keys=[user1_id])
    user2    = db.relationship("User", foreign_keys=[user2_id])
    messages = db.relationship("Message", backref="conversation", lazy="dynamic",
                               order_by="Message.date_envoi")

    __table_args__ = (
        db.UniqueConstraint("user1_id", "user2_id", name="uq_conv"),
    )


# ── Message ──────────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = "messages"
    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    expediteur_id   = db.Column(db.Integer, db.ForeignKey("users.id"),         nullable=False)
    contenu         = db.Column(db.Text, nullable=False)
    lu              = db.Column(db.Boolean, default=False)
    date_envoi      = db.Column(db.DateTime, default=datetime.utcnow)

    expediteur = db.relationship("User", foreign_keys=[expediteur_id])
