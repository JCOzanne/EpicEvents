from controllers.contract_controller import ContractController
from controllers.user_controller import UserController


class ContractView:
    def __init__(self, current_user):
        self.controller = ContractController()
        self.current_user = current_user
        self.user_controller = UserController()

    def check_authentication(self):
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
        print("\=== LISTE DES CONTRATS NON PAYES ENTIEREMENT ===")
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
        print("\ ===CREATION D'UN CONTRAT ===")
        client_id = input("ID du client: ")

        while True:
            amount_str = input("Montant du contrat: ")
            amount = validate_amount(amount_str)
            if amount is not None:
                break

        while True:
            sold_str = input("Montant déjà payé: ")
            sold = validate_amount(sold_str)
            if sold is not None and sold <= amount:
                break
            print("Le montant payé ne peut pas dépasser le montant du contrat.")

        status = input("Statut du contrat (1= signé, 0= non signé): ") =="1"

        contract = self.controller.create_contract(int(client_id), amount, sold, status, self.current_user)
        if contract:
            print(f"Contrat créé avec succès ")
        else:
            print("Erreur lors de la création du contrat.")

    def update_contract_prompt(self):
        print("\=== MISE A JOUR D'UN CONTRAT ===")
        contract_id = input("ID du contrat à mettre à jour: ")
        contract = self.controller.get_contract_by_id(int(contract_id))
        if not contract :
            print("Pas de contrat avec cet ID")
            return
        if self.current_user.role.name == 'commercial'and contract.client.commercial.id != self.current_user.id:
            print("Vous n'avez pas les droits pour mettre à jour ce contrat")
            return
        print(f"Date de création : {contract.date_created}, "
              f"Montant total : {contract.amount}, "
              f"Solde restant : {contract.sold}, "
              f"Statut : {'Signé' if contract.status else 'Non signé'}")

        amount = None
        amount_input = input("Nouveau montant total (laisser vide pour ne pas changer): ")
        if amount_input:
            amount = validate_amount(amount_input)
            if amount is None:
                return

        sold = None
        sold_input = input("Nouveau solde restant (laisser vide pour ne pas changer): ")
        if sold_input:
            sold = validate_amount(sold_input)
            if sold is None or (amount is not None and sold > amount):
                print("⚠️ Le solde restant ne peut pas dépasser le montant total.")
                return

        status = input("Statut du contrat (1 = signé, 0 = non signé, laisser vide pour ne pas changer): ")

        updated_contract = self.controller.update_contract(
            int(contract_id),
            float(amount) if amount else None,
            float(sold) if sold else None,
            status == "1" if status else None,
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

        contract_id = input("Saisissez l'ID du contrat à supprimer: ")

        if self.controller.delete_contract(int(contract_id), self.current_user):
            print("Contrat supprimé avec succès.")
        else:
            print("Échec de la suppression du contrat.")

def validate_amount(input_str):
    try:
        input_str = input_str.replace(',', '.')
        amount = float(input_str)
        if amount < 0:
            print("Le montant ne peut pas être négatif.")
            return None
        return amount
    except ValueError:
        print("Veuillez entrer un montant valide (nombre uniquement, sans symboles).")
        return None
            