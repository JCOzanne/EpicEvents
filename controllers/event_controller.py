from db.database import SessionLocal
from models.contracts import Contract
from models.events import Event

class EventController:
    def __init__(self):
        self.session = SessionLocal()

    def create_event(self, name, location, attendees, notes, start_date, end_date, contract_id, current_user):
        contract = self.session.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            print("Le contrat spécifié n'existe pas.")
            return None
        if not contract.status:
            print("Le contrat doit être signé pour créer un évènement")
            return None
        if current_user.role.name != "commercial":
            print("Seuls les commerciaux peuvent créer des évènements")
            return None
        client = contract.client
        if client.commercial_id != current_user.id:
            print("Vous ne pouvez créer un événement que pour vos propres clients.")
            return None

        new_event = Event(
            name=name,
            location=location,
            attendees=attendees,
            notes=notes,
            start_date=start_date,
            end_date=end_date,
            contract_id=contract_id,
            support_id=None
        )
        self.session.add(new_event)
        self.session.commit()
        print("Événement créé avec succès.")
        return new_event

    def update_events(self,
                      event_id,
                      name=None,
                      location=None,
                      attendees=None,
                      notes=None,
                      start_date=None,
                      end_date=None,
                      support_id=None,
                      current_user=None
                      ):
        event = self.session.query(Event).filter(Event.id == event_id).first()
        if not event:
            print("L'évènement n'existe pas")
            return None
        if current_user.role.name != 'gestion' and (event.support_id is None or event.support_id != current_user.id):
            print("Vous n'avez pas les droits pour modifier cet événement.")
            return None

        if name: event.name = name
        if location: event.location = location
        if attendees: event.attendees = attendees
        if notes: event.notes = notes
        if start_date: event.start_date = start_date
        if end_date: event.end_date = end_date
        if support_id: event.support_id = support_id

        self.session.commit()
        print("Événement mis à jour avec succès.")
        return event

    def delete_event(self, event_id, current_user):
        if current_user.role.name != 'gestion':
            print("Seuls les gestionnaires peuvent supprimer un évènement")
            return False
        event=self.session.query(Event).filter(Event.id == event_id).first()
        if not event:
            print("Événement introuvable.")
            return False

        self.session.delete(event)
        self.session.commit()
        print(f"L'évènement {event.name} a été supprimé avec succès.")
        return True


    def get_all_events(self):
        return self.session.query(Event).all()

    def get_events_by_support(self, support_id):
        """
        Retrieve all events associated with a specific support person.

        This method queries the database for events linked to a given support ID.

        """
        return self.session.query(Event).filter(Event.support_id == support_id).all()
