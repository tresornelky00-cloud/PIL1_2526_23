"""
routes/auth.py — Inscription, connexion, déconnexion
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))

    if request.method == "POST":
        nom       = request.form.get("nom", "").strip()
        prenom    = request.form.get("prenom", "").strip()
        email     = request.form.get("email", "").strip().lower()
        telephone = request.form.get("telephone", "").strip()
        filiere   = request.form.get("filiere")
        niveau    = request.form.get("niveau")
        password  = request.form.get("mot_de_passe", "")
        confirm   = request.form.get("confirm_mdp", "")

        # Validations
        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template("inscription.html")
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("inscription.html")
        if User.query.filter_by(telephone=telephone).first():
            flash("Ce numéro de téléphone est déjà utilisé.", "danger")
            return render_template("inscription.html")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            nom=nom, prenom=prenom, email=email,
            telephone=telephone, filiere=filiere,
            niveau=niveau, mot_de_passe=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Compte créé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return render_template("inscription.html")


@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profil.dashboard"))

    if request.method == "POST":
        identifiant = request.form.get("identifiant", "").strip().lower()
        password    = request.form.get("mot_de_passe", "")

        # Recherche par email ou téléphone
        user = User.query.filter(
            (User.email == identifiant) | (User.telephone == identifiant)
        ).first()

        if user and bcrypt.check_password_hash(user.mot_de_passe, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("profil.dashboard"))
        else:
            flash("Identifiant ou mot de passe incorrect.", "danger")

    return render_template("login.html")


@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("auth.login"))
