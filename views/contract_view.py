from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from controllers.client_controller import ClientController
from controllers.contract_controller import ContractController
from controllers.user_controller import UserController


class ContractView:
    def __init__(self, current_user):
        self.controller = ContractController()
        self.current_user = current_user
        self.user_controller = UserController()
        self.client_controller = ClientController()

    def check_authentication(self):
        """Checks user authentication.

        Verifies if a user is authenticated by checking for a valid token.
        If a valid token is found, the current_user attribute is updated
        and the function returns True. Otherwise, it returns False.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        from auth import verify_token
        payload = verify_token()
        if payload:
            self.current_user = self.controller.get_user_by_id(payload['user_id'])
            return True
        return False

    def display_contracts(self):
        contracts = self.controller.get_all_contracts()
        print("\n=== LISTE DES CONTRATS ===")
        for contract in contracts:
            client_name = contract.client.name if contract.client else "Client inconnu"
            client_phone = contract.client.phone if contract.client else "Non disponible"
            client_email = contract.client.email if contract.client else "Non disponible"
            commercial_name = contract.client.commercial.name if contract.client and contract.client.commercial else "Commercial inconnu"
            print(f"ID : {contract.id}, "
                  f"Client : {client_name}, "
                  f"Téléphone du client : {client_phone}, Email du client : {client_email}, "
                  f"Montant du contrat : {contract.amount},"
                  f"Reste à payer : {contract.sold} ,"
                  f"Status : {'signé' if contract.status else 'Non signé'},"
                  f"Contrat signé le : {contract.date_created}"
                  f"Commercial associé : {commercial_name}, "
                  )

    def display_unsigned_contracts(self):
        contracts = self.controller.get_unsigned_contracts()
        print("\n=== LISTE DES CONTRATS NON SIGNES ===")
        if not contracts:
            print("Aucun contrat non signé")
            return
        for contract in contracts:
            print(f"ID du contrat: {contract.id}, Client: {contract.client.name}, Montant: {contract.amount}, "
                  f"Solde: {contract.sold}, Date de création: {contract.date_created}")

    def display_unpaid_contracts(self):
        contracts = self.controller.get_unpaid_contracts()
        print("=== LISTE DES CONTRATS NON PAYES ENTIEREMENT ===")
        if not contracts:
            print("Les contrats ont été entièrement payés")
            return
        for contract in contracts:
            print(f"ID du contrat: {contract.id}, "
                  f"Client: {contract.client.name}, Montant: {contract.amount}, "
                  f"Solde: {contract.sold}"
                  f"Date de création : {contract.date_created}"
                  )

    def create_contract_prompt(self):
        if self.current_user.role.name != "gestion":
            print("Vous n'avez pas le droit de créer de contrat")
            return

        print("\n=== CREATION D'UN CONTRAT ===")

        clients = self.client_controller.get_all_clients()
        if not clients:
            print("Aucun client disponible. Veuillez d'abord créer un client.")
            return

        client_choices = [Choice(value=client.id, name=f"{client.name} ({client.company})") for client in clients]

        client_id = inquirer.select(
            message="Sélectionnez un client:",
            choices=client_choices,
        ).execute()

        def validate_amount(amount):

            """
            Validate the contract amount.

            This method checks if the given amount is a positive number.
            It returns True if the amount is valid (a number),
            otherwise it returns the validation error message.
            """
            try:
                amount = float(amount.replace(',', '.'))
                if amount <= 0:
                    return "Le montant doit être supérieur à zéro."
                return True
            except ValueError:
                return "Veuillez entrer un montant valide (nombre uniquement)."

        amount = inquirer.text(
            message="Montant total du contrat:",
            validate=validate_amount,
        ).execute()
        amount = float(amount.replace(',', '.'))

        def validate_sold(sold):
            try:
                sold = float(sold.replace(',', '.'))
                if sold < 0:
                    return "Le montant payé ne peut pas être négatif."
                if sold > amount:
                    return "Le montant payé ne peut pas dépasser le montant total du contrat."
                return True
            except ValueError:
                return "Veuillez entrer un montant valide (nombre uniquement)."

        sold = inquirer.text(
            message="Montant déjà payé:",
            validate=validate_sold,
        ).execute()
        sold = float(sold.replace(',', '.'))

        status = inquirer.confirm(
            message="Le contrat est-il signé?",
            default=False,
        ).execute()

        contract = self.controller.create_contract(client_id, amount, sold, status, self.current_user)
        if contract:
            print(f"Contrat créé avec succès pour le client ID {client_id}")
        else:
            print("Erreur lors de la création du contrat.")

    def update_contract_prompt(self):
        print("\n=== MISE A JOUR D'UN CONTRAT ===")

        contracts = self.controller.get_all_contracts()
        if not contracts:
            print("Aucun contrat disponible à mettre à jour.")
            return

        if self.current_user.role.name == 'commercial':
            contracts = [c for c in contracts if c.client and c.client.commercial_id == self.current_user.id]
            if not contracts:
                print("Vous n'avez aucun contrat associé à vos clients.")
                return

        contract_choices = [
            Choice(
                value=contract.id,
                name=f"ID: {contract.id}, Client: {contract.client.name if contract.client else 'Inconnu'}, Montant: {contract.amount}, Solde: {contract.sold}"
            )
            for contract in contracts
        ]

        contract_id = inquirer.select(
            message="Sélectionnez un contrat à mettre à jour:",
            choices=contract_choices,
        ).execute()

        contract = self.controller.get_contract_by_id(contract_id)
        print(f"Date de création : {contract.date_created}, "
              f"Montant total : {contract.amount}, "
              f"Solde restant : {contract.sold}, "
              f"Statut : {'Signé' if contract.status else 'Non signé'}")

        def validate_optional_amount(amount):
            if not amount:
                return True
            try:
                amount = float(amount.replace(',', '.'))
                if amount <= 0:
                    return "Le montant doit être supérieur à zéro."
                return True
            except ValueError:
                return "Veuillez entrer un montant valide (nombre uniquement)."

        amount_input = inquirer.text(
            message="Nouveau montant total (laisser vide pour ne pas changer):",
            validate=validate_optional_amount,
        ).execute()

        amount = float(amount_input.replace(',', '.')) if amount_input else None

        def validate_optional_sold(sold):
            if not sold:
                return True
            try:
                sold = float(sold.replace(',', '.'))
                if sold < 0:
                    return "Le montant payé ne peut pas être négatif."
                if amount is not None and sold > amount:
                    return "Le solde restant ne peut pas dépasser le montant total."
                if amount is None and sold > contract.amount:
                    return "Le solde restant ne peut pas dépasser le montant total actuel."
                return True
            except ValueError:
                return "Veuillez entrer un montant valide (nombre uniquement)."

        sold_input = inquirer.text(
            message="Nouveau solde restant (laisser vide pour ne pas changer):",
            validate=validate_optional_sold,
        ).execute()

        sold = float(sold_input.replace(',', '.')) if sold_input else None

        status_choices = [
            Choice(value=None, name="Ne pas modifier"),
            Choice(value=True, name="Signé"),
            Choice(value=False, name="Non signé"),
        ]

        status = inquirer.select(
            message="Nouveau statut du contrat:",
            choices=status_choices,
        ).execute()

        updated_contract = self.controller.update_contract(
            contract_id,
            amount,
            sold,
            status,
            self.current_user
        )

        if updated_contract:
            print("Contrat mis à jour avec succès!")
        else:
            print("Erreur lors de la mise à jour du contrat.")

    def delete_contract_prompt(self):
        if self.current_user.role.name != 'gestion':
            print("Vous n'avez pas les droits pour supprimer un contrat.")
            return

        print("\n=== SUPPRESSION D'UN CONTRAT ===")

        contracts = self.controller.get_all_contracts()
        if not contracts:
            print("Aucun contrat disponible à supprimer.")
            return

        contract_choices = [
            Choice(
                value=contract.id,
                name=f"ID: {contract.id}, Client: {contract.client.name if contract.client else 'Inconnu'}, Montant: {contract.amount}"
            )
            for contract in contracts
        ]

        contract_id = inquirer.select(
            message="Sélectionnez un contrat à supprimer:",
            choices=contract_choices,
        ).execute()

        confirm = inquirer.confirm(
            message=f"Êtes-vous sûr de vouloir supprimer le contrat {contract_id} ?",
            default=False,
        ).execute()

        if confirm and self.controller.delete_contract(contract_id, self.current_user):
            print("Contrat supprimé avec succès.")
        else:
            print("Suppression annulée ou erreur lors de la suppression.")
