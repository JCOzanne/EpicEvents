import pendulum

from db.database import SessionLocal
from models.clients import Client


class ClientController:
    def __init__(self):
        self.session = SessionLocal()

    def create_client(self, name, email, phone, company, current_user):
        if current_user.role.name != "commercial":
            return None

        new_client = Client(
            name=name,
            email=email,
            phone=phone,
            company=company,
            date_created=pendulum.today().to_date_string(),
            date_updated=pendulum.today().to_date_string(),
            commercial_id=current_user.id
        )
        self.session.add(new_client)
        self.session.commit()
        return new_client

    def update_client(self, client_id, name, email,  phone, company, current_user):
        client = self.get_client_by_id(client_id)
        if not client or client.commercial_id != current_user.id:
            return None
        if name :
            client.name = name
        if email :
            client.email = email
        if phone :
            client.phone = phone
        if company :
            client.company = company

        client.date_updated = pendulum.today().to_date_string()
        self.session.commit()
        return client

    def delete_client(self, client_id, current_user):
        client = self.get_client_by_id(client_id)
        if not client or client.commercial_id != current_user.id:
            return False

        self.session.delete(client)
        self.session.commit()
        return True


    def get_all_clients(self):
        return self.session.query(Client).all()

    def get_client_by_id(self, client_id):
        return self.session.query(Client).filter(Client.id == client_id).first()

    def get_client_by_commercial(self, commercial_id):
        return self.session.query(Client).filter(Client.commercial_id == commercial_id).all()
