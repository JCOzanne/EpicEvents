class MenuView:
    def __init__(self, user_view):
        self.user_view = user_view
        # Ajoutez ici les autres vues dont vous aurez besoin
        # self.client_view = client_view
        # self.contract_view = contract_view
        # self.event_view = event_view

    def display_main_menu(self):
        while True:
            print("\n=== EPIC EVENTS CRM ===")
            print("1. Gestion des utilisateurs")
            print("2. Gestion des clients")
            print("3. Gestion des contrats")
            print("4. Gestion des événements")
            print("0. Quitter")

            choice = input("Votre choix: ")

            if choice == "1":
                self.display_user_menu()
            elif choice == "2":
                # Appeler la méthode pour gérer les clients
                pass
            elif choice == "3":
                # Appeler la méthode pour gérer les contrats
                pass
            elif choice == "4":
                # Appeler la méthode pour gérer les événements
                pass
            elif choice == "0":
                print("Au revoir!")
                break
            else:
                print("Choix invalide. Veuillez réessayer.")

    def display_user_menu(self):
        """Affichage du menu de gestion des utilisateurs"""
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