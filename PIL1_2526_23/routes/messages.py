"""
routes/messages.py — Messagerie instantanée (Flask-SocketIO)
"""
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room
from models import db
from app import socketio
from models import User, Conversation, Message

messages_bp = Blueprint("messages", __name__)


def get_or_create_conversation(user1_id: int, user2_id: int) -> Conversation:
    conv = Conversation.query.filter(
        ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
        ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
    ).first()
    if not conv:
        conv = Conversation(user1_id=user1_id, user2_id=user2_id)
        db.session.add(conv)
        db.session.commit()
    return conv


def room_id(conv_id: int) -> str:
    return f"conv_{conv_id}"


@messages_bp.route("/messages")
@login_required
def liste():
    convs = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) |
        (Conversation.user2_id == current_user.id)
    ).all()

    conversations = []
    for conv in convs:
        interlocuteur = conv.user2 if conv.user1_id == current_user.id else conv.user1
        dernier_msg   = conv.messages.order_by(Message.date_envoi.desc()).first()
        nb_non_lus    = Message.query.filter_by(
            conversation_id=conv.id, lu=False
        ).filter(Message.expediteur_id != current_user.id).count()
        conversations.append({
            "conv": conv,
            "interlocuteur": interlocuteur,
            "dernier_msg": dernier_msg,
            "non_lus": nb_non_lus,
        })

    conversations.sort(
        key=lambda c: c["dernier_msg"].date_envoi if c["dernier_msg"] else c["conv"].date_creation,
        reverse=True
    )
    return render_template("messages.html", conversations=conversations)


@messages_bp.route("/messages/<int:user_id>")
@login_required
def ouvrir_conversation(user_id):
    interlocuteur = db.get_or_404(User, user_id)
    conv = get_or_create_conversation(current_user.id, interlocuteur.id)

    Message.query.filter_by(
        conversation_id=conv.id,
        lu=False
    ).filter(
        Message.expediteur_id == interlocuteur.id
    ).update({"lu": True})
    db.session.commit()

    historique = conv.messages.order_by(Message.date_envoi.asc()).all()

    return render_template(
        "conversation.html",
        interlocuteur=interlocuteur,
        conv=conv,
        historique=historique,
    )


@socketio.on("rejoindre")
def on_rejoindre(data):
    join_room(room_id(data["conv_id"]))


@socketio.on("envoyer_message")
def on_message(data):
    conv = db.session.get(Conversation, data["conv_id"])
    if conv is None:
        return
    if current_user.id not in (conv.user1_id, conv.user2_id):
        return

    msg = Message(
        conversation_id=conv.id,
        expediteur_id=current_user.id,
        contenu=data["contenu"].strip(),
    )
    db.session.add(msg)
    db.session.commit()

    emit("nouveau_message", {
        "id":            msg.id,
        "contenu":       msg.contenu,
        "expediteur_id": msg.expediteur_id,
        "prenom":        current_user.prenom,
        "nom":           current_user.nom,
        "date_envoi":    msg.date_envoi.strftime("%H:%M"),
    }, room=room_id(conv.id))
