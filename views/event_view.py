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

        def validate_date_format(date_str):
            if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
                return "Vous devez saisir une date au format JJ/MM/AAAA."
            try:
                day, month, year = map(int, date_str.split('/'))
                date = pendulum.date(year, month, day)

                if date < pendulum.today().date():
                    return "La date ne peut pas être dans le passé. Veuillez entrer une date future."

                return True
            except ValueError:
                return "Date invalide. Veuillez vérifier la validité du jour, du mois et de l'année."

        start_date_str = inquirer.text(
            message="Date de début (JJ/MM/AAAA): ",
            validate=validate_date_format
        ).execute()

        day, month, year = map(int, start_date_str.split('/'))
        start_date = pendulum.date(year, month, day)

        def validate_end_date(date_str):
            result = validate_date_format(date_str)
            if result is not True:
                return result

            day, month, year = map(int, date_str.split('/'))
            end_date = pendulum.date(year, month, day)

            if end_date < start_date:
                return "La date de fin doit être égale ou postérieure à la date de début."

            return True

        end_date_str = inquirer.text(
            message="Date de fin (JJ/MM/AAAA): ",
            validate=validate_end_date
        ).execute()

        day, month, year = map(int, end_date_str.split('/'))
        end_date = pendulum.date(year, month, day)

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

        modify_start_date = inquirer.confirm(
            message="Voulez-vous modifier la date de début ?",
            default=False
        ).execute()

        start_date = None
        if modify_start_date:
            def validate_date_format(date_str):
                """
                Validate the end date for an event.

                This method checks if the provided end date string is in the correct format (DD/MM/YYYY),
                is a valid date, is not in the past, and is not before the start date.
                """
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
                    return "Vous devez saisir une date au format JJ/MM/AAAA."
                try:
                    day, month, year = map(int, date_str.split('/'))
                    date = pendulum.date(year, month, day)

                    if date < pendulum.today().date():
                        return "La date ne peut pas être dans le passé. Veuillez entrer une date future."

                    return True
                except ValueError:
                    return "Date invalide. Veuillez vérifier la validité du jour, du mois et de l'année."

            start_date_str = inquirer.text(
                message="Nouvelle date de début (JJ/MM/AAAA): ",
                validate=validate_date_format
            ).execute()

            day, month, year = map(int, start_date_str.split('/'))
            start_date = pendulum.date(year, month, day)

        modify_end_date = inquirer.confirm(
            message="Voulez-vous modifier la date de fin ?",
            default=False
        ).execute()

        end_date = None
        if modify_end_date:
            def validate_end_date(date_str):
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
                    return "Vous devez saisir une date au format JJ/MM/AAAA."
                try:
                    day, month, year = map(int, date_str.split('/'))
                    date = pendulum.date(year, month, day)

                    if date < pendulum.today().date():
                        return "La date ne peut pas être dans le passé. Veuillez entrer une date future."

                    if start_date and date < start_date:
                        return "La date de fin doit être égale ou postérieure à la date de début."

                    return True
                except ValueError:
                    return "Date invalide. Veuillez vérifier la validité du jour, du mois et de l'année."

            end_date_str = inquirer.text(
                message="Nouvelle date de fin (JJ/MM/AAAA): ",
                validate=validate_end_date
            ).execute()

            day, month, year = map(int, end_date_str.split('/'))
            end_date = pendulum.date(year, month, day)

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
        """
        Display events assigned to the current support user.

        This method retrieves and displays the events associated
        with the current user if their role is 'support'.
        """
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
