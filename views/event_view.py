import re
import pendulum
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.base.control import Choice

from controllers.event_controller import EventController
from controllers.user_controller import UserController


class EventView:
    def __init__(self, current_user):
        self.controller = EventController()
        self.current_user = current_user
        self.user_controller = UserController()

    def check_authentication(self):
        from auth import verify_token
        payload = verify_token()
        if payload:
            self.current_user = self.controller.get_user_by_id(payload['user_id'])
            return True
        return False

    def prompt_valid_date(self, message, min_date=None, after_date=None):
        if min_date and isinstance(min_date, pendulum.DateTime):
            min_date = min_date.date()
        if after_date and isinstance(after_date, pendulum.DateTime):
            after_date = after_date.date()

        while True:
            date_str = inquirer.text(message=message).execute()

            if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
                print("❌ Format invalide. Utilisez JJ/MM/AAAA.")
                continue

            try:
                day, month, year = map(int, date_str.split('/'))
                date = pendulum.date(year, month, day)
            except ValueError:
                print("❌ Date invalide. Veuillez vérifier le jour, le mois et l'année.")
                continue

            if min_date and date < min_date:
                print("❌ La date ne peut pas être dans le passé.")
                continue

            if after_date and date < after_date:
                print("❌ La date doit être égale ou postérieure à la date de début.")
                continue

            return date

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

        name = inquirer.text(
            message="Nom de l'événement",
            validate=EmptyInputValidator("Le nom de l'événement ne peut être vide.")
        ).execute()
        location = inquirer.text(
            message="Lieu de l'événement",
            validate=EmptyInputValidator("Le lieu de l'événement ne peut être vide")
        ).execute()
        attendees = inquirer.text(
            message="Nombre de participants à l'événement",
            validate=EmptyInputValidator("Le nombre de participants ne peut être vide")
        ).execute()
        notes = inquirer.text(
            message="Notes concernant l'événement"
        ).execute()

        start_date = self.prompt_valid_date("Date de début (JJ/MM/AAAA):", min_date=pendulum.today())
        end_date = self.prompt_valid_date("Date de fin (JJ/MM/AAAA):", min_date=pendulum.today(), after_date=start_date)

        contract_id = inquirer.number(
            message="ID du contrat associé: ",
            validate=EmptyInputValidator("L'ID du contrat associé ne peut être vide.")
        ).execute()

        self.controller.create_event(name, location, attendees, notes, start_date, end_date, contract_id,
                                     self.current_user)

    def update_event_prompt(self):
        events = self.controller.get_all_events()
        if not events:
            print("Aucun événement à modifier.")
            return

        print("\n=== MISE À JOUR D'UN ÉVÉNEMENT ===")

        event_choices = [Choice(value=event.id, name=f"ID: {event.id}, Nom: {event.name}, Lieu: {event.location}") for
                         event in events]

        event_id = inquirer.select(
            message="Sélectionnez l'événement à modifier:",
            choices=event_choices
        ).execute()

        print("Laissez les champs vides pour ne pas modifier les valeurs actuelles.")

        name = inquirer.text(
            message="Nom de l'événement: "
        ).execute()

        location = inquirer.text(
            message="Lieu: "
        ).execute()

        attendees_str = inquirer.text(
            message="Nombre de participants: "
        ).execute()

        attendees = int(attendees_str) if attendees_str and attendees_str.isdigit() else None

        notes = inquirer.text(
            message="Notes: "
        ).execute()

        start_date = None
        if inquirer.confirm(message="Voulez-vous modifier la date de début ?", default=False).execute():
            start_date = self.prompt_valid_date("Nouvelle date de début (JJ/MM/AAAA):", min_date=pendulum.today())

        end_date = None
        if inquirer.confirm(message="Voulez-vous modifier la date de fin ?", default=False).execute():
            end_date = self.prompt_valid_date("Nouvelle date de fin (JJ/MM/AAAA):", min_date=pendulum.today(), after_date=start_date)

        support_id_str = inquirer.text(
            message="ID du support assigné (laissez vide pour ne pas modifier): "
        ).execute()

        support_id = int(support_id_str) if support_id_str and support_id_str.isdigit() else None

        self.controller.update_events(
            event_id,
            name if name else None,
            location if location else None,
            attendees,
            notes if notes else None,
            start_date,
            end_date,
            support_id,
            self.current_user
        )

    def delete_event_prompt(self):
        if self.current_user.role.name != 'gestion':
            print("Vous n'avez pas les droits pour supprimer un événement")
            return

        events = self.controller.get_all_events()
        if not events:
            print("Aucun événement à supprimer.")
            return

        print("\n=== SUPPRESSION D'UN ÉVÉNEMENT ===")

        event_choices = [Choice(value=event.id, name=f"ID: {event.id}, Nom: {event.name}, Lieu: {event.location}") for
                         event in events]

        event_id = inquirer.select(
            message="Sélectionnez l'événement à supprimer:",
            choices=event_choices
        ).execute()

        confirm = inquirer.confirm(
            message=f"Êtes-vous sûr de vouloir supprimer l'événement {event_id} ?",
            default=False
        ).execute()

        if confirm and self.controller.delete_event(event_id, self.current_user):
            print("Événement supprimé avec succès.")
        else:
            print("Suppression annulée ou échec de la suppression.")

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
