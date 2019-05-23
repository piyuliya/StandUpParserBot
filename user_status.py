from db import User, session


def save_user(chat_id):
    new_chat_id = session.query(User.chat_id)\
        .filter(User.chat_id == chat_id).count()
    if not new_chat_id:
        new_user = User(
            chat_id=chat_id,
            subscribe=True,
            )
        session.add(new_user)
        session.commit()
    else:
        session.query(User.chat_id, User.subscribe)\
            .filter(User.chat_id == chat_id).update({"subscribe": True})
        session.commit()


def remove_user(chat_id):
    session.query(User.chat_id, User.subscribe)\
        .filter(User.chat_id == chat_id).update({"subscribe": False})
    session.commit()


session.close()
