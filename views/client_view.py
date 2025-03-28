import re

from controllers.client_controller import ClientController
from controllers.user_controller import UserController


class ClientView:
    def __init__(self, client):
        self.controller = ClientController()
        self.current_user = None
        self.user_controller = UserController()

    def check_authentication(self):
        from auth import verify_token
        payload = verify_token()
        if payload:
            self.current_user = self.controller.get_user_by_id(payload['user_id'])
            return True
        return False

    def display_clients(self):
        clients = self.controller.get_all_clients()
        print("\n=== LISTE DES CLIENTS ===")
        for client in clients:
            print(f"ID: {client.id}, Nom: {client.name}, "
                  f"Email: {client.email}, Téléphone: {client.phone},"
                  f" Entreprise : {client.company},"
                  f" Date de création: {client.date_created},"
                  f" Date de modification: {client.date_updated},")
            commercial_name = client.commercial.name if client.commercial else "Pas de commercial attribué"
            print(f"Contact commercial chez epic Events : {commercial_name}")

    def create_client_prompt(self):
        if not self.current_user or self.current_user.role.name != 'commercial':
            print("Vous n'avez pas les droits pour créer un client")
            return
        print ("\n=== CRÉATION D'UN CLIENT ===")
        name = input("Nom du client: ")
        email = input("Email du client: ")
        while True:
            phone = input("Numéro de téléphone (format: 10 chiffres sans espaces ni - ou /) : ")
            if validate_phone(phone):
                break
        company = input("Entreprise du client: ")
        client = self.controller.create_client(name, email, phone, company, self.current_user)
        if client:
            print(f"Client {client.name} crée avec succés")
        else:
            print("Erreur lors de la création du client")

    def update_client_prompt(self):
        if not self.current_user or self.current_user.role != 'commercial':
            print("Vous n'avez pas les droits pour modifier un client")
            return

        print("\n=== MISE À JOUR D'UN CLIENT ===")
        client_id = input("ID du client à modifier : ")
        client = self.controller.get_client_by_id(int(client_id))

        if not client or client.commercial_id != self.current_user.id:
            print("Vous ne pouvez modifier que vos propres clients")
            return
        name = input("Nouveau nom du client (laisser vide pour ne pas changer): ")
        email = input("Nouvel email du client (laisser vide pour ne pas changer) : ")

        phone = None
        phone_input = input("Nouveau numéro de téléphone (format: 10 chiffres sans espaces ni - ou /): ")
        if phone_input and validate_phone(phone_input):
            phone = phone_input
        company = input("Nouvelle entreprise du client (laisser vide pour ne pas changer): ")

        updated_client = self.controller.update_client(client.id, name, email, phone, company, self.current_user)
        if updated_client:
            print(f"Client {updated_client.name} mis à jour avec succès!")
        else:
            print("Erreur lors de la mise à jour du client.")

    def delete_client_prompt(self):
        if not self.current_user or self.current_user.role != 'commercial':
            print("Vous n'avez pas les drois pour supprimer un client")
            return

        print("\n=== SUPPRESSION D'UN CLIENT ===")
        client_id = input("ID du client à supprimer: ")

        if self.controller.delete_client(int(client_id), self.current_user):
            print("Client supprimé avec succès!")
        else:
            print("Erreur lors de la suppression du client.")

    def display_clients_by_commercial(self):
        if not self.current_user or self.current_user.role.name != "commercial":
            print("Vous n'avez pas les droits pour voir cette liste.")
            return

        clients = self.controller.get_client_by_commercial(self.current_user.id)
        print("\n=== VOS CLIENTS ===")
        if not clients:
            print("Aucun client associé.")
            return

        for client in clients:
            print(f"ID: {client.id}, Nom: {client.name}, Email: {client.email}, Entreprise: {client.company}")

def validate_phone(phone):
    pattern = r'^0[1-9]\d{8}$'
    if re.fullmatch(pattern, phone):
        return True
    print("Le numéro de téléphone doit être composé de 10 chiffres (sans espaces, - ou /) et commencer par 0.")
    return False
