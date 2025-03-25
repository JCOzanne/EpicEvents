import re
import pendulum

from controllers.event_controller import EventController


class EventView:
    def __init__(self, current_user):
        self.controller = EventController()
        self.current_user = current_user

    def display_events(self):
        events = self.controller.get_all_events()
        print("\n=== LISTE DES ÉVÉNEMENTS ===")
        if not events:
            print("Aucun événement trouvé.")
            return

        for event in events:
            print(f"ID de l'événement: {event.id}, "
                  f"Nom de l'événement: {event.name}, "
                  f"Lieu de l'événement: {event.location}, "
                  f"Nombre de participants: {event.attendees},"
                  f"Notes: {event.notes}, "
                  f"Date de début: {event.start_date}, "
                  f"Date de fin: {event.end_date},"
                  f"Support: {event.support.name if event.support else 'Non assigné'}")

    def create_event_prompt(self):
        if self.current_user.role.name != 'commercial':
            print("Vous n'avez pas les droits pour créer un événement.")
            return

        print("\n=== CRÉATION D'UN ÉVÉNEMENT ===")
        name = input("Nom de l'événement: ")
        location = input("Lieu: ")
        attendees = int(input("Nombre de participants: "))
        notes = input("Notes: ")
        while True:
            start_date_str = input("Date de début (JJ/MM/AAAA): ")
            start_date = validate_date(start_date_str)
            if start_date:
                break
        while True:
            end_date_str = input("Date de fin (JJ/MM/AAAA): ")
            end_date = validate_date(end_date_str)
            if end_date and end_date >= start_date:
                break
            print("La date de fin doit être égale ou postérieure à la date de début.")

        contract_id = int(input("ID du contrat associé: "))

        self.controller.create_event(name, location, attendees, notes, start_date, end_date, contract_id, self.current_user)

    def update_event_prompt(self):
        event_id = int(input("ID de l'événement à modifier: "))

        print("Laissez vide pour ne pas modifier.")
        name = input("Nom de l'événement: ") or None
        location = input("Lieu: ") or None
        attendees = input("Nombre de participants: ")
        attendees = int(attendees) if attendees else None
        notes = input("Notes: ") or None
        start_date=None
        end_date=None
        if input("Voulez-vous modifier la date de début ? (o/n): ").lower() == 'o':
            while True:
                start_date_str = input("Nouvelle date de début (JJ/MM/AAAA): ")
                start_date = validate_date(start_date_str)
                if start_date:
                    break

        if input("Voulez-vous modifier la date de fin ? (o/n): ").lower() == 'o':
            while True:
                end_date_str = input("Nouvelle date de fin (JJ/MM/AAAA): ")
                end_date = validate_date(end_date_str)
                if end_date and (not start_date or end_date >= start_date):
                    break
                print("La date de fin doit être égale ou postérieure à la date de début.")

        support_id = input("ID du support assigné: ")
        support_id = int(support_id) if support_id else None

        self.controller.update_events(event_id, name, location, attendees, notes,
                                      start_date, end_date, support_id, self.current_user)

    def delete_event_prompt(self):
        if self.current_user.role.name != 'gestion':
            print("Vous n'avez pas les droits pour supprimer un événement")
            return
        event_id = input("Saississez l'ID de l'événement à supprimer: ")
        if self.controller.delete_event(int(event_id), self.current_user):
            print("Événement supprimé avec succés")
        else:
            print("Echec de la suppression de l'événement")

    def display_events_by_support(self):
        if self.current_user.role.name != 'support':
            print("Vous n'avez pas les droits pour afficher ces événements.")
            return

        events = self.controller.get_events_by_support(self.current_user.id)
        print("\n=== VOS ÉVÉNEMENTS ===")
        if not events:
            print("Aucun événement trouvé.")
            return

        for event in events:
            print(f"ID: {event.id}, "
                  f"Nom: {event.name}, "
                  f"Lieu: {event.location}, "
                  f"Nombre de participants: {event.attendees},"
                  f"Notes: {event.notes}, "
                  f"Date de début: {event.start_date}, "
                  f"Date de fin: {event.end_date}")

def validate_date(date_str):
    """
    Validates if a date is in DD/MM/YYYY format and if it is in the future.
    :param date_str: The date entered by the user (str)
    :return: Pendulum Date if valid, None otherwise
    """
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        print(" Vous devez saisir une date au format JJ/MM/AAAA.")
        return None
    try:
        day, month, year = map(int, date_str.split('/'))
        date = pendulum.date(year, month, day)
    except ValueError:
        print("Date invalide. Veuillez vérifier la validité du jour, du mois et de l'année.")
        return None

    if date < pendulum.today().date():
        print("La date ne peut pas être dans le passé. Veuillez entrer une date future.")
        return None
    return date