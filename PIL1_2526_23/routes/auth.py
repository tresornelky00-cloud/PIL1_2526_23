"""
routes/auth.py — Inscription, connexion, déconnexion
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import time
from models import db
from app import bcrypt
from models import User, Competence, UserCompetence, Disponibilite

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))
    return render_template("index.html")

@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))
    if request.method == "POST":
        nom       = request.form.get("nom", "").strip()
        prenom    = request.form.get("prenom", "").strip()
        email     = request.form.get("email", "").strip().lower()
        telephone = request.form.get("telephone", "").strip()
        filiere   = request.form.get("filiere") or "GL"
        niveau    = request.form.get("niveau") or "L1"
        bio       = request.form.get("bio", "").strip() or None
        password  = request.form.get("mot_de_passe", "")
        confirm   = request.form.get("confirm_mdp", "")

        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template("inscription.html")
        if len(password) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères.", "danger")
            return render_template("inscription.html")
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("inscription.html")
        if User.query.filter_by(telephone=telephone).first():
            flash("Ce numéro est déjà utilisé.", "danger")
            return render_template("inscription.html")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(nom=nom, prenom=prenom, email=email, telephone=telephone,
                    filiere=filiere, niveau=niveau, mot_de_passe=hashed_pw, bio=bio)
        db.session.add(user)
        db.session.flush()

        for nom_c in [c.strip() for c in request.form.get("maitrisees_txt","").split(",") if c.strip()]:
            comp = Competence.query.filter_by(nom=nom_c).first()
            if not comp:
                comp = Competence(nom=nom_c, categorie="Autre"); db.session.add(comp); db.session.flush()
            db.session.add(UserCompetence(user_id=user.id, competence_id=comp.id, type="maitrise"))

        for nom_c in [c.strip() for c in request.form.get("lacunes_txt","").split(",") if c.strip()]:
            comp = Competence.query.filter_by(nom=nom_c).first()
            if not comp:
                comp = Competence(nom=nom_c, categorie="Autre"); db.session.add(comp); db.session.flush()
            db.session.add(UserCompetence(user_id=user.id, competence_id=comp.id, type="lacune"))

        for j, d, f in zip(request.form.getlist("jours[]"), request.form.getlist("debut[]"), request.form.getlist("fin[]")):
            try:
                db.session.add(Disponibilite(user_id=user.id, jour=j,
                    heure_debut=time(*map(int,d.split(":"))),
                    heure_fin=time(*map(int,f.split(":")))))
            except: pass

        db.session.commit()
        flash("Compte créé ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))
    return render_template("inscription.html")

@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))
    if request.method == "POST":
        ident    = request.form.get("identifiant","").strip().lower()
        password = request.form.get("mot_de_passe","")
        user = User.query.filter((User.email==ident)|(User.telephone==ident)).first()
        if user and bcrypt.check_password_hash(user.mot_de_passe, password):
            login_user(user)
            return redirect(request.args.get("next") or url_for("profil.dashboard"))
        flash("Identifiant ou mot de passe incorrect.", "danger")
    return render_template("login.html")

@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("auth.login"))
