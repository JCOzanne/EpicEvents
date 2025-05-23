import os
import re
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator

from views.client_view import ClientView
from views.contract_view import ContractView
from views.event_view import EventView
from auth import TOKEN_FILE


class MenuView:
    def __init__(self, user_view):
        self.user_view = user_view
        self.token_file = TOKEN_FILE
        self.client_view = ClientView(user_view.current_user)
        self.contract_view = ContractView(user_view.current_user)
        self.event_view = EventView(user_view.current_user)
        self.current_user = self.load_user_from_token()

    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return "Veuillez entrer un email valide"
        return True

    def load_user_from_token(self):
        """
        Loads user data from a saved token.

        Attempts to load a user from a token stored in a file. If the token exists and is valid,
        the corresponding user is returned and a success message is printed. If the token is
        invalid or doesn't exist, None is returned.

        Returns: User or None: The loaded user object if successful, None otherwise.
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as file:
                token = file.read().strip()
                user = self.user_view.controller.verify_token(token)
                if user:
                    print(f"Connexion rétablie pour {user.name} ({user.role.name})")
                    return user
        return None

    def save_token(self, token):
        with open(self.token_file, "w") as file:
            file.write(token)

    def delete_token(self):
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            print("Déconnexion réussie.")
        else:
            print("Aucun token trouvé. Vous n'êtes pas connecté.")

    def display_main_menu(self):
        while True:
            print("\n=== EPIC EVENTS CRM ===")
            if self.current_user:
                choices = [
                    Choice(value="1", name="Gestion des utilisateurs"),
                    Choice(value="2", name="Gestion des clients"),
                    Choice(value="3", name="Gestion des contrats"),
                    Choice(value="4", name="Gestion des événements"),
                    Choice(value="5", name="Se déconnecter"),
                ]
            else:
                choices = [
                    Choice(value="1", name="Se connecter"),
                    Choice(value="0", name="Quitter"),
                ]

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=choices,
            ).execute()

            if not self.current_user:
                if choice == "1":
                    self.login_prompt()
                elif choice == "0":
                    print("Au revoir !")
                    break
            else:
                if choice == "1":
                    self.display_user_menu()
                elif choice == "2":
                    self.display_client_menu()
                elif choice == "3":
                    self.display_contract_menu()
                elif choice == "4":
                    self.display_event_menu()
                elif choice == "5":
                    self.delete_token()
                    self.current_user = None

    def login_prompt(self):
        print("=== CONNEXION ===")

        email = inquirer.text(message="Email: ",
                              validate=self.validate_email,
                              ).execute()
        password = inquirer.secret(message="Mot de passe: ",
                                   validate=EmptyInputValidator(message="Le mot de passe ne peut être vide"),
                                   ).execute()
        user = self.user_view.controller.authenticate(email, password)
        if user:
            print(f"Bienvenue {user.name} !")
            token = self.user_view.controller.generate_token(user)
            self.save_token(token)
            self.current_user = user
        else:
            print("Email ou mot de passe incorrect.")

    def display_user_menu(self):
        while True:
            print("\n=== GESTION DES UTILISATEURS ===")

            choices = [
                Choice(value="1", name="Afficher tous les utilisateurs"),
                Choice(value="2", name="Créer un utilisateur"),
                Choice(value="3", name="Mettre à jour un utilisateur"),
                Choice(value="4", name="Supprimer un utilisateur"),
                Choice(value="0", name="Retour au menu principal"),
            ]

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=choices,
            ).execute()

            if choice == "1":
                self.user_view.display_users()
            elif choice == "2":
                self.user_view.create_user_prompt()
            elif choice == "3":
                self.user_view.update_user_prompt()
            elif choice == "4":
                self.user_view.delete_user_prompt()
            elif choice == "0":
                break

    def display_client_menu(self):
        while True:
            print("\n=== GESTION DES CLIENTS ===")

            choices = [
                Choice(value="1", name="Afficher tous les clients"),
                Choice(value="2", name="Afficher mes clients (commerciaux uniquement)"),
                Choice(value="3", name="Créer un client"),
                Choice(value="4", name="Mettre à jour un client"),
                Choice(value="5", name="Supprimer un client"),
                Choice(value="0", name="Retour au menu principal"),
            ]

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=choices,
            ).execute()

            if choice == "1":
                self.client_view.display_clients()
            elif choice == "2":
                self.client_view.display_clients_by_commercial()
            elif choice == "3":
                self.client_view.create_client_prompt()
            elif choice == "4":
                self.client_view.update_client_prompt()
            elif choice == "5":
                self.client_view.delete_client_prompt()
            elif choice == "0":
                break
            else:
                print("Choix invalide. Veuillez réessayer.")

    def display_contract_menu(self):
        while True:
            print("\n=== GESTION DES CONTRATS ===")

            choices = [
                Choice(value="1", name="Afficher tous les contrats"),
                Choice(value="2", name="Afficher les contrats non signés"),
                Choice(value="3", name="Afficher les contrats non entièrement payés"),
                Choice(value="4", name="Créer un contrat"),
                Choice(value="5", name="Mettre à jour un contrat"),
                Choice(value="6", name="Supprimer un contrat"),
                Choice(value="0", name="Retour au menu principal"),
            ]

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=choices,
            ).execute()

            if choice == "1":
                self.contract_view.display_contracts()
            elif choice == "2":
                self.contract_view.display_unsigned_contracts()
            elif choice == "3":
                self.contract_view.display_unpaid_contracts()
            elif choice == "4":
                self.contract_view.create_contract_prompt()
            elif choice == "5":
                self.contract_view.update_contract_prompt()
            elif choice == "6":
                self.contract_view.delete_contract_prompt()
            elif choice == "0":
                break
            else:
                print("Choix invalide. Veuillez réessayer.")

    def display_event_menu(self):
        while True:
            print("\n=== GESTION DES ÉVÉNEMENTS ===")

            choices = [
                Choice(value="1", name="Afficher tous les événements"),
                Choice(value="2", name="Afficher les événements attribués (support uniquement)"),
                Choice(value="3", name="Créer un événement (commercial uniquement)"),
                Choice(value="4", name="Mettre à jour un événement"),
                Choice(value="5", name="Supprimer un événement"),
                Choice(value="0", name="Retour au menu principal"),
            ]

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=choices,
            ).execute()

            if choice == "1":
                self.event_view.display_events()
            elif choice == "2":
                self.event_view.display_events_by_support()
            elif choice == "3":
                self.event_view.create_event_prompt()
            elif choice == "4":
                self.event_view.update_event_prompt()
            elif choice == "5":
                self.event_view.delete_event_prompt()
            elif choice == "0":
                break
            else:
                print("Choix invalide. Veuillez réessayer.")
