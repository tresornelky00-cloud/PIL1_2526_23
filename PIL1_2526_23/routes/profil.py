from datetime import time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models import User, Competence, UserCompetence, Disponibilite, OffreMentorat, Match, Conversation
from algo_matching import proposer_matchs

profil_bp = Blueprint("profil", __name__)

@profil_bp.route("/dashboard")
@login_required
def dashboard():
    from datetime import datetime
    offres    = current_user.offres.filter_by(active=True).all()
    matchs_c  = Match.query.filter((Match.mentor_id==current_user.id)|(Match.mentore_id==current_user.id)).count()
    convs_c   = Conversation.query.filter((Conversation.user1_id==current_user.id)|(Conversation.user2_id==current_user.id)).count()
    suggestions = proposer_matchs(current_user, top_n=4)
    mait = current_user.competences.filter_by(type="maitrise").count()
    lac  = current_user.competences.filter_by(type="lacune").count()
    fields = [current_user.bio, mait > 0, lac > 0, current_user.disponibilites.count() > 0]
    profil_pct = 50 + int(sum(bool(f) for f in fields) / len(fields) * 50)
    return render_template("dashboard.html", offres=offres, matchs_count=matchs_c,
                           convs_count=convs_c, suggestions=suggestions,
                           profil_pct=profil_pct, now=datetime.now())

@profil_bp.route("/profil", methods=["GET","POST"])
@login_required
def profil():
    toutes = Competence.query.order_by(Competence.categorie).all()
    if request.method == "POST":
        current_user.bio     = request.form.get("bio","").strip() or None
        current_user.filiere = request.form.get("filiere")
        current_user.niveau  = request.form.get("niveau")
        UserCompetence.query.filter_by(user_id=current_user.id).delete()
        for cid in request.form.getlist("maitrisees"):
            db.session.add(UserCompetence(user_id=current_user.id, competence_id=int(cid), type="maitrise"))
        for cid in request.form.getlist("lacunes"):
            if cid not in request.form.getlist("maitrisees"):
                db.session.add(UserCompetence(user_id=current_user.id, competence_id=int(cid), type="lacune"))
        Disponibilite.query.filter_by(user_id=current_user.id).delete()
        for j, d, f in zip(request.form.getlist("jours[]"), request.form.getlist("debut[]"), request.form.getlist("fin[]")):
            try:
                db.session.add(Disponibilite(user_id=current_user.id, jour=j,
                    heure_debut=time(*map(int,d.split(":"))),
                    heure_fin=time(*map(int,f.split(":")))))
            except: pass
        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for("profil.profil"))
    mait_ids = {uc.competence_id for uc in current_user.competences.filter_by(type="maitrise")}
    lac_ids  = {uc.competence_id for uc in current_user.competences.filter_by(type="lacune")}
    return render_template("profil.html", competences=toutes, maitrisees_ids=mait_ids,
                           lacunes_ids=lac_ids, dispos=current_user.disponibilites.all())

@profil_bp.route("/offre/nouvelle", methods=["GET","POST"])
@login_required
def nouvelle_offre():
    competences = Competence.query.all()
    if request.method == "POST":
        db.session.add(OffreMentorat(
            user_id=current_user.id,
            type_offre=request.form.get("type_offre"),
            competence_id=int(request.form.get("competence_id")),
            format=request.form.get("format"),
            description=request.form.get("description","").strip() or None
        ))
        db.session.commit()
        flash("Offre publiée.", "success")
        return redirect(url_for("profil.dashboard"))
    return render_template("nouvelle_offre.html", competences=competences)

@profil_bp.route("/offre/<int:offre_id>/supprimer", methods=["POST"])
@login_required
def supprimer_offre(offre_id):
    offre = db.get_or_404(OffreMentorat, offre_id)
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
    user = db.get_or_404(User, user_id)
    return render_template("voir_profil.html", user=user)
