"""
routes/matching.py — Suggestions de matching, offres, contact
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models import User, OffreMentorat, Competence, Match
from matching import proposer_matchs

matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/matching")
@login_required
def index():
    """Affiche les suggestions de mentors pour le mentoré connecté."""
    suggestions = proposer_matchs(current_user, top_n=10)
    return render_template("matching.html", suggestions=suggestions)


@matching_bp.route("/matching/contacter/<int:mentor_id>", methods=["POST"])
@login_required
def contacter(mentor_id):
    """Crée ou retrouve la conversation avec ce mentor et redirige."""
    from routes.messages import get_or_create_conversation
    mentor = db.get_or_404(User, mentor_id)
    conv = get_or_create_conversation(current_user.id, mentor.id)

    match_existe = Match.query.filter_by(
        mentor_id=mentor.id, mentore_id=current_user.id
    ).first()
    if not match_existe:
        from matching import calculer_score
        score = calculer_score(mentor, current_user)
        db.session.add(Match(
            mentor_id=mentor.id,
            mentore_id=current_user.id,
            score=score,
            statut="propose"
        ))
        db.session.commit()

    return redirect(url_for("messages.ouvrir_conversation", user_id=mentor.id))


@matching_bp.route("/offres")
@login_required
def liste_offres():
    """Liste toutes les offres actives, avec filtres optionnels."""
    filiere  = request.args.get("filiere", "")
    comp_id  = request.args.get("competence", type=int)
    type_off = request.args.get("type_offre", "")

    query = OffreMentorat.query.filter_by(active=True)

    if filiere:
        query = query.join(User, OffreMentorat.user_id == User.id)\
                     .filter(User.filiere == filiere)
    if comp_id:
        query = query.filter(OffreMentorat.competence_id == comp_id)
    if type_off:
        query = query.filter(OffreMentorat.type_offre == type_off)

    offres      = query.order_by(OffreMentorat.date_creation.desc()).all()
    competences = Competence.query.order_by(Competence.nom).all()

    return render_template("offres.html", offres=offres, competences=competences,
                           filiere=filiere, comp_id=comp_id, type_off=type_off)
