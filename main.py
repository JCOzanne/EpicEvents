import bcrypt

from models.roles import Role
from models.users import User
from models.clients import Client
from models.contracts import Contract
from models.events import Event
from views.menu_view import MenuView
from views.user_view import UserView
from db.database import engine, Base, SessionLocal


def initialize_roles():
    session = SessionLocal()

    if session.query(Role).count() == 0:
        commercial = Role(name="commercial")
        support = Role(name="support")
        gestion = Role(name="gestion")

        session.add_all([commercial, support, gestion])
        session.commit()

        print("Rôles initialisés avec succès.")

    session.close()


def create_admin_user():
    session = SessionLocal()

    if session.query(User).filter(User.email == "admin@epicevents.com").count() == 0:
        gestion_role = session.query(Role).filter(Role.name == "gestion").first()

        password_bytes = "adminpassword".encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        admin = User(
            name="Admin",
            email="admin@epicevents.com",
            password=hashed_password,
            role_id=gestion_role.id
        )

        session.add(admin)
        session.commit()

        print("Utilisateur admin créé avec succès.")

    session.close()

def main():
    Base.metadata.create_all(engine)
    initialize_roles()
    create_admin_user()

    print("Application démarrée.")


    user_view = UserView()

    if user_view.login_prompt():
        menu_view = MenuView(user_view)
        menu_view.display_main_menu()
    else:
        print("Connexion échouée. Veuillez réessayer.")

if __name__ == "__main__":
    main()