import re
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator

from controllers.client_controller import ClientController
from controllers.user_controller import UserController


class ClientView:
    def __init__(self, current_user=None):
        self.controller = ClientController()
        self.current_user = current_user
        self.user_controller = UserController()

    def check_authentication(self):
        from auth import verify_token
        payload = verify_token()
        if payload:
            self.current_user = self.controller.get_user_by_id(payload['user_id'])
            return True
        return False

    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return "Veuillez entrer un email valide"
        return True

    def validate_phone(self, phone):
        pattern = r'^0[1-9]\d{8}$'
        if re.fullmatch(pattern, phone):
            return True
        print("Le numéro de téléphone doit être composé de 10 chiffres (sans espaces, - ou /) et commencer par 0.")
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
        name = inquirer.text(
            message="Nom du client: ",
            validate=EmptyInputValidator("Le nom ne peut pas être vide."),
        ).execute()

        email = inquirer.text(
            message="Email: ",
            validate=self.validate_email,
        ).execute()

        phone = inquirer.text(
            message="Numéro de téléphone: ",
            validate=self.validate_phone,
        ).execute()

        company = inquirer.text(
            message="Nom de la société: ",
            validate=EmptyInputValidator("Le nom de la société ne peut pas être vide."),
        ).execute()

        client = self.controller.create_client(name, email, phone, company, self.current_user)
        if client:
            print(f"Le client {client.name} a été créé avec succès.")
        else:
            print("Erreur lors de la création du client.")

    def update_client_prompt(self):
        clients = self.controller.get_all_clients()
        if not clients:
            print("Aucun client à mettre à jour.")
            return

        print("\n=== MISE À JOUR D'UN CLIENT ===")

        client_choices = [Choice(value=client.id, name=f"{client.name} ({client.company})") for client in clients]
        client_id = inquirer.select(
            message="Sélectionnez un client à mettre à jour: ",
            choices=client_choices,
        ).execute()

        name = inquirer.text(
            message="Nouveau nom (laisser vide pour ne pas changer):",
        ).execute()

        def validate_optional_email(email):
            return True if not email else self.validate_email(email)

        email = inquirer.text(
            message="Nouvel email (laisser vide pour ne pas changer):",
            validate=validate_optional_email,
        ).execute()

        def validate_optional_phone(phone: object) -> bool:
            return True if not phone else self.validate_phone(phone)

        phone = inquirer.text(
            message="Nouveau téléphone (laisser vide pour ne pas changer):",
            validate=validate_optional_phone,
        ).execute()

        company = inquirer.text(
            message="Nouvelle société (laisser vide pour ne pas changer):",
        ).execute()

        client = self.controller.update_client(client_id, name or None, email or None, phone or None, company or None,
                                               self.current_user)
        if client:
            print(f"Le client {client.name} a été mis à jour avec succès.")
        else:
            print("Erreur lors de la mise à jour du client.")

    def delete_client_prompt(self):
        clients = self.controller.get_all_clients()
        if not clients:
            print("Aucun client à supprimer.")
            return

        print("\n=== SUPPRESSION D'UN CLIENT ===")

        client_choices = [Choice(value=client.id, name=f"{client.name} ({client.company})") for client in clients]
        client_id = inquirer.select(
            message="Sélectionnez un client à supprimer: ",
            choices=client_choices,
        ).execute()

        confirm = inquirer.confirm(
            message=f"Êtes-vous sûr de vouloir supprimer le client {client_id} ?",
            default=False,
        ).execute()

        if confirm and self.controller.delete_client(client_id, self.current_user):
            print("Le client a été supprimé avec succès.")
        else:
            print("Suppression annulée ou erreur lors de la suppression.")

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

