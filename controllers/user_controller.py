import bcrypt

from models.users import User
from models.roles import Role
from db.database import SessionLocal


class UserController:
    def __init__(self):
        self.session = SessionLocal()

    def hash_password(self, password):
        """
        Secure password hashing with bcrypt
        :param password:
        :return:hashed_password
        """
        password_bytes = password.encode('utf-8') if isinstance(password, str) else password
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed_password

    def verify_password(self, stored_password, provided_password):
        """
        Password verification with bcrypt
        :param stored_password:
        :param provided_password:
        :return:Boolean
        """
        provided_password_bytes = provided_password.encode('utf-8') if isinstance(provided_password, str) else provided_password
        return bcrypt.checkpw(provided_password_bytes, stored_password)

    def create_user(self, name, email, password, role_id, current_user_id):
        if not self.check_permission(current_user_id, "gestion"):
            return None

        hashed_password = self.hash_password(password)
        new_user = User(name=name, email=email, password=hashed_password, role_id=role_id)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def authenticate(self, email, password):
        """
        User authentication
        :param email:
        :param password:
        :return:user or None
        """
        user = self.session.query(User).filter(User.email == email).first()
        if user and self.verify_password(user.password, password):
            return user
        return None

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_all_users(self):
        return self.session.query(User).all()

    def update_user(self, user_id, current_user_id, name=None, email=None, role_id=None):
        if not self.check_permission(current_user_id, "gestion"):
            return None

        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if name:
            user.name = name
        if email:
            user.email = email
        if role_id:
            user.role_id = role_id

        self.session.commit()
        return user

    def delete_user(self, user_id, current_user_id):
        if not self.check_permission(current_user_id, "gestion"):
            return False

        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    def check_permission(self, user_id, role_name):
        """
        Checking a user's permissions
        :param user_id:
        :param role_name:
        :return: user's role
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        role = self.session.query(Role).filter(Role.id == user.role_id).first()
        return role.name == role_name
