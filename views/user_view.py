from controllers.user_controller import UserController
from auth import generate_token, verify_token, delete_token

class UserView:
    def __init__(self):
        self.controller = UserController()
        self.current_user = None

    def login_prompt(self):
        print("=== CONNEXION ===")
        email = input("Email: ")
        password = input("Mot de passe: ")

        user = self.controller.authenticate(email, password)
        if user:
            self.current_user = user
            generate_token(user)
            print(f"Bienvenue, {user.name}!")
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
        name = input("Nom: ")
        email = input("Email: ")
        password = input("Mot de passe: ")

        print("Rôles disponibles:")
        print("1. Commercial")
        print("2. Support")
        print("3. Gestion")
        role_choice = input("Choix du rôle (1-3): ")

        role_id = int(role_choice)

        user = self.controller.create_user(name, email, password, role_id, self.current_user.id)
        if user:
            print(f"Utilisateur {user.name} créé avec succès!")
        else:
            print("Erreur lors de la création de l'utilisateur.")

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
        user_id = input("ID de l'utilisateur à mettre à jour: ")
        try:
            user_id = int(user_id)
        except ValueError:
            print("ID invalide. Veuillez entrer un nombre entier.")
            return
        name = input("Nouveau nom (laissez vide pour ne pas changer): ")
        email = input("Nouvel email (laissez vide pour ne pas changer): ")

        print("Rôles disponibles:")
        print("1. Commercial")
        print("2. Support")
        print("3. Gestion")
        role_choice = input("Nouveau rôle (1-3, laissez vide pour ne pas changer): ")

        role_id = int(role_choice) if role_choice else None

        user = self.controller.update_user(
            int(user_id),
            self.current_user.id,
            name if name else None,
            email if email else None,
            role_id if role_id else None
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
        user_id = input("ID de l'utilisateur à supprimer: ")

        if self.controller.delete_user(int(user_id), self.current_user.id):
            print("Utilisateur supprimé avec succès!")
        else:
            print("Erreur lors de la suppression de l'utilisateur.")
