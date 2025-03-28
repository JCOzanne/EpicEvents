import os

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

    def load_user_from_token(self):
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
                print("1. Gestion des utilisateurs")
                print("2. Gestion des clients")
                print("3. Gestion des contrats")
                print("4. Gestion des événements")
                print("5. Se déconnecter")
            else:
                print("1. Se connecter")
                print("0. Quitter")

            choice = input("Votre choix: ")

            if not self.current_user:
                if choice == "1":
                    self.login_prompt()
                elif choice == "0":
                    print("Au revoir !")
                    break
                else:
                    print("Choix invalide. Veuillez réessayer.")
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
                else:
                    print("Choix invalide. Veuillez réessayer.")

    def login_prompt(self):
        print("=== CONNEXION ===")
        email = input("Email: ")
        password = input("Mot de passe: ")

        user = self.user_view.controller.authenticate(email, password)
        if user:
            print(f"Bienvenue, {user.name}!")
            token = self.user_view.controller.generate_token(user)
            self.save_token(token)
            self.current_user = user
        else:
            print("⚠️ Email ou mot de passe incorrect.")

    def display_user_menu(self):
        while True:
            print("\n=== GESTION DES UTILISATEURS ===")
            print("1. Afficher tous les utilisateurs")
            print("2. Créer un utilisateur")
            print("3. Mettre à jour un utilisateur")
            print("4. Supprimer un utilisateur")
            print("0. Retour au menu principal")

            choice = input("Votre choix: ")

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
            else:
                print("Choix invalide. Veuillez réessayer.")

    def display_client_menu(self):
        while True:
            print("\n=== GESTION DES CLIENTS ===")
            print("1. Afficher tous les clients")
            print("2. Afficher mes clients (commerciaux uniquement)")
            print("3. Créer un client")
            print("4. Mettre à jour un client")
            print("5. Supprimer un client")
            print("0. Retour au menu principal")

            choice = input("Votre choix: ")

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
            print("1. Afficher tous les contrats")
            print("2. Afficher les contrats non signés")
            print("3. Afficher les contrats non entièrement payés")
            print("4. Créer un contrat")
            print("5. Mettre à jour un contrat")
            print("6. Supprimer un contrat")
            print("0. Retour au menu principal")

            choice = input("Votre choix: ")

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
            print("1. Afficher tous les événements")
            print("2. Afficher les événements attribués (support uniquement)")
            print("3. Créer un événement (commercial uniquement)")
            print("4. Mettre à jour un événement")
            print("5. Supprimer un événement")
            print("0. Retour au menu principal")

            choice = input("Votre choix: ")

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
