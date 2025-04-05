import pendulum
import sentry_sdk

from db.database import SessionLocal
from models.contracts import Contract


class ContractController:
    def __init__(self):
        self.session = SessionLocal()

    def create_contract(self, client_id, amount, sold, status, current_user):
        if current_user.role.name != "gestion":
            return None

        new_contract = Contract(
            client_id=client_id,
            amount=amount,
            sold=sold,
            status=status,
            date_created=pendulum.today().to_date_string()
            )
        self.session.add(new_contract)
        self.session.commit()
        if status:
            sentry_sdk.capture_message(
                f"[CONTRAT] Contrat {new_contract.id} signé pour le client {client_id} "
                f"par {current_user.email} (Montant: {amount})",
                level="info"
            )
        print("Contrat crée avec succés")
        return new_contract

    def update_contract(self, contract_id, amount, sold, status, current_user):
        contract = self.get_contract_by_id(contract_id)
        if not contract:
            return None

        if current_user.role.name != "gestion" and contract.client.commercial_id != current_user.id:
            return None

        if amount is not None:
            contract.amount = amount
        if sold is not None:
            contract.sold = sold
        if status is not None:
            contract.status = status

        self.session.commit()
        return contract

    def delete_contract(self, contract_id, current_user):
        if current_user.role.name != "gestion":
            print("Seuls les gestionnaires peuvent supprimer un contrat.")
            return False

        contract = self.get_contract_by_id(contract_id)
        if not contract:
            print("contrat introuvable.")
            return False

        self.session.delete(contract)
        self.session.commit()
        print(f"Le contrat ID {contract.id} a été supprimé avec succès.")
        return True

    def get_all_contracts(self):
        return self.session.query(Contract).all()

    def get_contract_by_id(self, contract_id):
        return self.session.query(Contract).filter(Contract.id == contract_id).first()

    def get_contracts_by_commercial(self, commercial_id):
        return (
            self.session.query(Contract)
            .join(Contract.client)
            .filter(Contract.client.commercial_id == commercial_id)
            .all()
        )

    def get_unsigned_contracts(self):
        return self.session.query(Contract).filter(Contract.status == 0).all()

    def get_unpaid_contracts(self):
        return self.session.query(Contract).filter(Contract.sold > 0).all()
