import bcrypt
import jwt
import os
import pendulum
from dotenv import load_dotenv
from models.users import User
from models.roles import Role
from db.database import SessionLocal

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_FILE = '.jwt_token'
TOKEN_EXPIRATION_MINUTES = 30
ALGORITHM = 'HS256'


class UserController:
    def __init__(self):
        self.session = SessionLocal()

    def hash_password(self, password: str) ->str:
        """
        Secure password hashing with bcrypt
        :param password:the password og the user
        :return:hashed_password
        """
        password_bytes = password.encode('utf-8') if isinstance(password, str) else password
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """
        Password verification with bcrypt
        :param stored_password: hashed password stored in the database
        :param provided_password: the password entered by the user
        :return:Boolean
        """
        provided_password_bytes = provided_password.encode('utf-8') if isinstance(provided_password, str) else provided_password
        return bcrypt.checkpw(provided_password_bytes, stored_password.encode('utf-8'))

    def create_user(self, name: str, email: str, password: str, role_id: int, current_user_id: int) -> User|None:
        if not self.check_permission(current_user_id, "gestion"):
            return None

        hashed_password = self.hash_password(password)
        new_user = User(name=name, email=email, password=hashed_password, role_id=role_id)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def authenticate(self, email: str, password: str) -> bool|None:
        """
        User authentication
        :param email: the email of the user
        :param password: the password of the user
        :return: user or None
        """
        user = self.session.query(User).filter(User.email == email).first()
        if user and self.verify_password(user.password, password):
            return user
        return None

    def get_user_by_id(self, user_id: int) -> User|None:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_all_users(self) -> list[User|None]:
        return self.session.query(User).all()

    def update_user(self, user_id: int, current_user_id: int, name=None, email=None, role_id=None) -> User|None:
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

    def delete_user(self, user_id: int, current_user_id: int) -> bool:
        if not self.check_permission(current_user_id, "gestion"):
            return False

        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    def check_permission(self, user_id: int, role_name: str) -> bool:
        """
        Checking a user's permissions
        :param user_id: the id of the user
        :param role_name: management/commercial/support
        :return: user's role
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        role = self.session.query(Role).filter(Role.id == user.role_id).first()
        return role.name == role_name

    def generate_token(self, user: 'User') -> str:
        expiration = pendulum.now().add(hours=1)
        payload = {
            'user_id': user.id,
            'role_id': user.role.name,
            'exp': expiration.int_timestamp,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        with open (TOKEN_FILE, "w") as file:
            file.write(token)
        print("Connexion réussie")
        return token

    def verify_token(self, token: str) -> bool|None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            return self.get_user_by_id(user_id)
        except jwt.ExpiredSignatureError:
            print("Le token a expiré. Veuillez vous reconnecter.")
            return None
        except jwt.InvalidTokenError:
            print("Token invalide.")
            return None
