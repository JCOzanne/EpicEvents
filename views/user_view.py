from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator
import re

from controllers.user_controller import UserController
from auth import generate_token, verify_token, delete_token

class UserView:
    def __init__(self):
        self.controller = UserController()
        self.current_user = None

    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return "Veuillez entrer un email valide"
        return True

    def login_prompt(self):
        print("=== CONNEXION ===")

        email = inquirer.text("Email: ",
                              validate=self.validate_email,
                              ).execute()
        password = inquirer.secret(
            message="Mot de passe: ",
            validate=EmptyInputValidator(message="Le mot de passe ne peut être vide"),
        ).execute()

        user=self.controller.authenticate(email, password)
        if user:
            self.current_user = user
            generate_token(user)
            print(f"Bienvenue {user.name} !")
            return True
        else:
            print("Email ou mot de passe incorrect.")
            return False

    def logout_prompt(self):
        delete_token()
        self.current_user = None
        print("Déconnexion réussie.")

    def check_authentication(self):
        payload = verify_token()
        if payload:
            self.current_user = self.controller.get_user_by_id(payload['user_id'])
            return True
        return False

    def create_user_prompt(self):
        if not self.current_user or not self.controller.check_permission(self.current_user.id, "gestion"):
            print("Vous n'avez pas les droits pour créer un utilisateur.")
            return

        print("=== CREATION D'UTILISATEUR ===")

        name=inquirer.text(message="Nom de l'utilisateur",
                           validate=EmptyInputValidator(message="Le nom ne peut pas être vide"),
                           ).execute()
        email=inquirer.text(message="Email: ",
                            validate=self.validate_email,
                            ).execute()
        password=inquirer.secret(
            message="Mot de passe: ",
            validate=EmptyInputValidator(message="Le mail ne peut être vide"),
        ).execute()
        role_choice=inquirer.select(
            message="Rôle",
            choices=[
                Choice(value=1, name="Commercial"),
                Choice(value=2, name="Support"),
                Choice(value=3, name="Gestion"),
            ],
        ).execute()

        user=self.controller.create_user(name, email, password, role_choice, self.current_user.id)
        if user:
            print(f"L'utilisateur {user.name} crée avec succés")
        else:
            print("Erreur lors de la création de l'utilisateur")

    def display_users(self):
        users = self.controller.get_all_users()

        print("=== LISTE DES UTILISATEURS ===")
        for user in users:
            print(f"ID: {user.id}, Nom: {user.name}, Email: {user.email}, Rôle: {user.role.name}")

    def update_user_prompt(self):
        if not self.current_user or not self.controller.check_permission(self.current_user.id, "gestion"):
            print("Vous n'avez pas les droits pour mettre à jour un utilisateur.")
            return

        print("=== MISE A JOUR D'UTILISATEUR ===")

        users = self.controller.get_all_users()
        user_choices = [Choice(value=user.id, name=f"ID: {user.id}, Nom: {user.name}, Email: {user.email}") for user in
                        users]

        user_id = inquirer.select(
            message="Sélectionnez l'utilisateur à mettre à jour:",
            choices=user_choices,
        ).execute()

        name = inquirer.text(
            message="Nouveau nom (laissez vide pour ne pas changer):",
        ).execute()

        def validate_optional_email(result):
            if not result:
                return True
            return self.validate_email(result)

        email = inquirer.text(
            message="Nouvel email (laissez vide pour ne pas changer):",
            validate=validate_optional_email,
        ).execute()

        role_choices = [
            Choice(value=None, name="Ne pas changer"),
            Choice(value=1, name="Commercial"),
            Choice(value=2, name="Support"),
            Choice(value=3, name="Gestion"),
        ]

        role_id = inquirer.select(
            message="Nouveau rôle:",
            choices=role_choices,
        ).execute()

        user = self.controller.update_user(
            user_id,
            self.current_user.id,
            name if name else None,
            email if email else None,
            role_id
        )

        if user:
            print(f"Utilisateur {user.name} mis à jour avec succès!")
        else:
            print("Erreur lors de la mise à jour de l'utilisateur.")



    def delete_user_prompt(self):
        if not self.current_user or not self.controller.check_permission(self.current_user.id, "gestion"):
            print("Vous n'avez pas les droits pour supprimer un utilisateur.")
            return

        print("=== SUPPRESSION D'UTILISATEUR ===")

        users = self.controller.get_all_users()
        user_choices = [Choice(value=user.id, name=f"ID: {user.id}, Nom: {user.name}, Email: {user.email}") for user in
                        users]

        user_id = inquirer.select(
            message="Sélectionnez l'utilisateur à supprimer:",
            choices=user_choices,
        ).execute()

        confirm = inquirer.confirm(
            message=f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user_id} ?",
            default=False
        ).execute()

        if not confirm:
            print("Suppression annulée.")
            return

        if self.controller.delete_user(user_id, self.current_user.id):
            print("Utilisateur supprimé avec succès!")
        else:
            print("Erreur lors de la suppression de l'utilisateur.")
