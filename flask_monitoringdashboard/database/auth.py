from flask_monitoringdashboard.database import User, session_scope
from flask_monitoringdashboard import config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from pymongo.errors import DuplicateKeyError


def update_user(new_password, old_password, user_id, user_is_admin):
    with session_scope() as session:
        if not getattr(User, "is_mongo_db", False):
            user = session.query(User).filter(User.id == user_id).one()
        else:
            try:
                user = User(**User().get_collection(session).find_one({"id": user_id}))
            except TypeError:
                raise NoResultFound()
        user.is_admin = user_is_admin
        if old_password:
            if user.check_password(old_password):
                user.set_password(new_password)
                if getattr(User, "is_mongo_db", False):
                    user.get_collection(session).update_one({"id": user_id}, {"$set": user})
                return True
            else:
                return False
        if getattr(User, "is_mongo_db", False):
            user.get_collection(session).update_one({"id": user_id}, {"$set": user})
        return True


def create_default_user(session):
    if getattr(User, "is_mongo_db", False):
        if User().get_collection(session).count_documents({}) == 0:
            user = User(username=config.username, is_admin=True)
            user.set_password(password=config.password)
            user.get_collection(session).insert_one(user)
    else:
        if session.query(User).count() == 0:
            user = User(username=config.username, is_admin=True)
            user.set_password(password=config.password)
            session.add(user)


def get_user(username, password):
    """Validates the username and password and returns an User-object if both are valid.
    In case the User-table is empty, a user with default credentials is added.
    """
    with session_scope() as session:
        create_default_user(session)
        if getattr(User, "is_mongo_db", False):
            try:
                user = User(**User().get_collection(session).find_one({"username": username}))
            except TypeError:
                user = None
        else:
            user = session.query(User).filter(User.username == username).one_or_none()
        if user is not None:
            if user.check_password(password=password):
                if not getattr(User, "is_mongo_db", False):
                    session.expunge_all()
                return user

    return None


def add_user(username, is_admin, password):
    with session_scope() as session:
        user = User(username=username, is_admin=is_admin)
        user.set_password(password=password)
        if getattr(User, "is_mongo_db", False):
            try:
                user.get_collection(session).insert_one(user)
            except DuplicateKeyError:
                raise IntegrityError(orig="add_user", params="user_id", statement="USER ALREADY EXIST")
        else:
            session.add(user)
            session.commit()


def delete_user(user_id):
    with session_scope() as session:
        if getattr(User, "is_mongo_db", False):
            User().get_collection(session).delete_one({"id": user_id})
        else:
            session.query(User).filter(User.id == user_id).delete()


def get_all_users():
    with session_scope() as session:
        if getattr(User, "is_mongo_db", False):
            users = list(User(**elem) for elem in User().get_collection(session).find({}).sort([("id", -1)]))
        else:
            users = session.query(User).order_by(User.id).all()

        return [
            {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
            }
            for user in users
        ]
