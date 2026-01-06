from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config
from datetime import datetime, timedelta
import os

class GoogleIntegration:
    """Intégration complète avec Google Workspace (Docs, Sheets, Calendar)"""

    def __init__(self):
        self.credentials = None
        self.docs_service = None
        self.sheets_service = None
        self.drive_service = None
        self.calendar_service = None
        self._setup_credentials()

    def _setup_credentials(self):
        """Configurer les credentials Google API"""
        credentials_file = os.path.join(os.path.dirname(__file__), '..', 'google_credentials.json')

        if os.path.exists(credentials_file):
            try:
                SCOPES = [
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/calendar'
                ]

                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_file, scopes=SCOPES
                )

                self.docs_service = build('docs', 'v1', credentials=self.credentials)
                self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
                self.drive_service = build('drive', 'v3', credentials=self.credentials)
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)

            except Exception as e:
                print(f"Erreur lors de la configuration des credentials: {e}")
                self.credentials = None

    # ===== GOOGLE CALENDAR =====

    def create_calendar_event(self, appointment):
        """Créer un événement dans Google Calendar"""
        if not self.calendar_service:
            raise Exception("Google Calendar API non configurée")

        try:
            patient = appointment.patient

            # Créer la date/heure de début
            start_datetime = datetime.combine(appointment.date, appointment.time)

            # Calculer la fin (début + durée)
            end_datetime = start_datetime + timedelta(minutes=appointment.duration)

            # Formater pour Google Calendar (RFC3339)
            start_str = start_datetime.isoformat()
            end_str = end_datetime.isoformat()

            # Créer l'événement
            event = {
                'summary': f'Séance - {patient.first_name} {patient.last_name}',
                'description': f'''Type: {appointment.therapy_type or 'Consultation'}
Durée: {appointment.duration} minutes
Notes: {appointment.notes or 'Aucune note'}''',
                'start': {
                    'dateTime': start_str,
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': end_str,
                    'timeZone': 'Europe/Paris',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 24h avant
                        {'method': 'popup', 'minutes': 60},  # 1h avant
                    ],
                },
            }

            # Ajouter le téléphone du patient si disponible
            if patient.phone:
                event['description'] += f'\nTél patient: {patient.phone}'

            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return created_event.get('id')

        except HttpError as error:
            raise Exception(f"Erreur lors de la création de l'événement: {error}")

    def update_calendar_event(self, event_id, appointment):
        """Mettre à jour un événement dans Google Calendar"""
        if not self.calendar_service:
            raise Exception("Google Calendar API non configurée")

        try:
            patient = appointment.patient

            start_datetime = datetime.combine(appointment.date, appointment.time)
            end_datetime = start_datetime + timedelta(minutes=appointment.duration)

            event = {
                'summary': f'Séance - {patient.first_name} {patient.last_name}',
                'description': f'''Type: {appointment.therapy_type or 'Consultation'}
Durée: {appointment.duration} minutes
Statut: {appointment.status}
Notes: {appointment.notes or 'Aucune note'}''',
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
            }

            if patient.phone:
                event['description'] += f'\nTél patient: {patient.phone}'

            updated_event = self.calendar_service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()

            return updated_event.get('id')

        except HttpError as error:
            raise Exception(f"Erreur lors de la mise à jour: {error}")

    def delete_calendar_event(self, event_id):
        """Supprimer un événement de Google Calendar"""
        if not self.calendar_service:
            raise Exception("Google Calendar API non configurée")

        try:
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True

        except HttpError as error:
            raise Exception(f"Erreur lors de la suppression: {error}")

    def get_upcoming_events(self, days=7):
        """Récupérer les événements à venir"""
        if not self.calendar_service:
            raise Exception("Google Calendar API non configurée")

        try:
            now = datetime.utcnow().isoformat() + 'Z'
            future = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=future,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])

        except HttpError as error:
            raise Exception(f"Erreur lors de la récupération: {error}")

    # ===== GOOGLE DOCS =====

    def create_session_document(self, session):
        """Créer un document Google Docs pour une séance"""
        if not self.docs_service:
            raise Exception("Google Docs API non configurée")

        try:
            title = f"Séance {session.patient.first_name} {session.patient.last_name} - {session.session_date.strftime('%d/%m/%Y')}"

            document = self.docs_service.documents().create(body={'title': title}).execute()
            doc_id = document.get('documentId')

            content = self._format_session_content(session)

            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            return doc_id

        except HttpError as error:
            raise Exception(f"Erreur lors de la création du document: {error}")

    def _format_session_content(self, session):
        """Formater le contenu de la séance pour Google Docs"""
        patient = session.patient

        content = f"""COMPTE-RENDU DE SÉANCE

Patient: {patient.first_name} {patient.last_name}
Date: {session.session_date.strftime('%d/%m/%Y')}
Type de thérapie: {session.therapy_type or 'Non spécifié'}
Numéro de séance: {session.session_number or 'N/A'}

"""

        if session.objectives:
            content += f"\nOBJECTIFS DE LA SÉANCE\n{session.objectives}\n"

        if session.interventions:
            content += f"\nINTERVENTIONS THÉRAPEUTIQUES\n{session.interventions}\n"

        if session.patient_progress:
            content += f"\nPROGRÈS OBSERVÉS\n{session.patient_progress}\n"

        if session.mood_score or session.anxiety_score:
            content += "\nÉVALUATIONS\n"
            if session.mood_score:
                content += f"Humeur: {session.mood_score}/10\n"
            if session.anxiety_score:
                content += f"Anxiété: {session.anxiety_score}/10\n"

        if session.homework:
            content += f"\nEXERCICES À FAIRE\n{session.homework}\n"

        if session.next_session_plan:
            content += f"\nPLAN POUR LA PROCHAINE SÉANCE\n{session.next_session_plan}\n"

        return content

    # ===== GOOGLE SHEETS =====

    def create_patient_spreadsheet(self, patient):
        """Créer une feuille de calcul Google Sheets pour suivre l'évolution d'un patient"""
        if not self.sheets_service:
            raise Exception("Google Sheets API non configurée")

        try:
            title = f"Suivi {patient.first_name} {patient.last_name}"

            spreadsheet = {
                'properties': {'title': title},
                'sheets': [
                    {
                        'properties': {
                            'title': 'Séances',
                            'gridProperties': {'rowCount': 100, 'columnCount': 10}
                        }
                    },
                    {
                        'properties': {
                            'title': 'Questionnaires',
                            'gridProperties': {'rowCount': 100, 'columnCount': 10}
                        }
                    }
                ]
            }

            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()

            spreadsheet_id = spreadsheet.get('spreadsheetId')
            self._add_spreadsheet_headers(spreadsheet_id)

            return spreadsheet_id

        except HttpError as error:
            raise Exception(f"Erreur lors de la création de la feuille: {error}")

    def _add_spreadsheet_headers(self, spreadsheet_id):
        """Ajouter les en-têtes aux feuilles"""
        session_headers = [
            'Date', 'Numéro', 'Type de thérapie', 'Objectifs',
            'Interventions', 'Progrès', 'Humeur (1-10)', 'Anxiété (1-10)',
            'Exercices', 'Prochaine séance'
        ]

        questionnaire_headers = [
            'Date', 'Questionnaire', 'Score total', 'Interprétation', 'Notes'
        ]

        requests = [
            {
                'updateCells': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': len(session_headers)
                    },
                    'rows': [{
                        'values': [{'userEnteredValue': {'stringValue': header}} for header in session_headers]
                    }],
                    'fields': 'userEnteredValue'
                }
            },
            {
                'updateCells': {
                    'range': {
                        'sheetId': 1,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': len(questionnaire_headers)
                    },
                    'rows': [{
                        'values': [{'userEnteredValue': {'stringValue': header}} for header in questionnaire_headers]
                    }],
                    'fields': 'userEnteredValue'
                }
            }
        ]

        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

    def add_session_to_spreadsheet(self, spreadsheet_id, session):
        """Ajouter une séance à la feuille de calcul"""
        if not self.sheets_service:
            raise Exception("Google Sheets API non configurée")

        try:
            values = [[
                session.session_date.strftime('%d/%m/%Y'),
                session.session_number or '',
                session.therapy_type or '',
                session.objectives or '',
                session.interventions or '',
                session.patient_progress or '',
                session.mood_score or '',
                session.anxiety_score or '',
                session.homework or '',
                session.next_session_plan or ''
            ]]

            body = {'values': values}

            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Séances!A2',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

        except HttpError as error:
            raise Exception(f"Erreur lors de l'ajout de la séance: {error}")

    def export_questionnaire_to_sheets(self, spreadsheet_id, response):
        """Exporter un questionnaire vers Google Sheets"""
        if not self.sheets_service:
            raise Exception("Google Sheets API non configurée")

        try:
            values = [[
                response.completed_at.strftime('%d/%m/%Y'),
                response.questionnaire.name,
                response.total_score or '',
                response.interpretation or '',
                response.notes or ''
            ]]

            body = {'values': values}

            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Questionnaires!A2',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

        except HttpError as error:
            raise Exception(f"Erreur lors de l'export du questionnaire: {error}")


# Alias pour compatibilité ascendante
GoogleDocsIntegration = GoogleIntegration
