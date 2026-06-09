"""
routes/profil.py — Dashboard, profil, compétences, disponibilités
"""
from datetime import time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, Competence, UserCompetence, Disponibilite, OffreMentorat

profil_bp = Blueprint("profil", __name__)


@profil_bp.route("/dashboard")
@login_required
def dashboard():
    offres = current_user.offres.filter_by(active=True).all()
    return render_template("dashboard.html", offres=offres)


@profil_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    toutes_competences = Competence.query.order_by(Competence.categorie).all()

    if request.method == "POST":
        # Mise à jour infos générales
        current_user.bio     = request.form.get("bio", "").strip()
        current_user.filiere = request.form.get("filiere")
        current_user.niveau  = request.form.get("niveau")

        # Compétences maîtrisées
        maitrisees = request.form.getlist("maitrisees")
        lacunes    = request.form.getlist("lacunes")

        # Supprime et recrée les compétences
        UserCompetence.query.filter_by(user_id=current_user.id).delete()
        for cid in maitrisees:
            db.session.add(UserCompetence(
                user_id=current_user.id,
                competence_id=int(cid),
                type="maitrise"
            ))
        for cid in lacunes:
            if cid not in maitrisees:   # pas les deux en même temps
                db.session.add(UserCompetence(
                    user_id=current_user.id,
                    competence_id=int(cid),
                    type="lacune"
                ))

        # Disponibilités
        Disponibilite.query.filter_by(user_id=current_user.id).delete()
        jours = request.form.getlist("jours[]")
        debuts = request.form.getlist("debut[]")
        fins   = request.form.getlist("fin[]")
        for j, d, f in zip(jours, debuts, fins):
            h_debut = time(*map(int, d.split(":")))
            h_fin   = time(*map(int, f.split(":")))
            db.session.add(Disponibilite(
                user_id=current_user.id,
                jour=j,
                heure_debut=h_debut,
                heure_fin=h_fin
            ))

        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for("profil.profil"))

    maitrisees_ids = {uc.competence_id for uc in
                      current_user.competences.filter_by(type="maitrise")}
    lacunes_ids    = {uc.competence_id for uc in
                      current_user.competences.filter_by(type="lacune")}
    dispos         = current_user.disponibilites.all()

    return render_template(
        "profil.html",
        competences=toutes_competences,
        maitrisees_ids=maitrisees_ids,
        lacunes_ids=lacunes_ids,
        dispos=dispos,
    )


@profil_bp.route("/offre/nouvelle", methods=["GET", "POST"])
@login_required
def nouvelle_offre():
    competences = Competence.query.all()
    if request.method == "POST":
        offre = OffreMentorat(
            user_id=current_user.id,
            type_offre=request.form.get("type_offre"),
            competence_id=int(request.form.get("competence_id")),
            format=request.form.get("format"),
            description=request.form.get("description", "").strip(),
        )
        db.session.add(offre)
        db.session.commit()
        flash("Offre publiée.", "success")
        return redirect(url_for("profil.dashboard"))
    return render_template("nouvelle_offre.html", competences=competences)


@profil_bp.route("/offre/<int:offre_id>/supprimer", methods=["POST"])
@login_required
def supprimer_offre(offre_id):
    offre = OffreMentorat.query.get_or_404(offre_id)
    if offre.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for("profil.dashboard"))
    offre.active = False
    db.session.commit()
    flash("Offre supprimée.", "info")
    return redirect(url_for("profil.dashboard"))


@profil_bp.route("/utilisateur/<int:user_id>")
@login_required
def voir_profil(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("voir_profil.html", user=user)
