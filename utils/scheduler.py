"""
Scheduler pour les tâches automatiques
- Envoi de rappels de rendez-vous
- Synchronisation Google Calendar
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_automatic_reminders(app):
    """Envoyer les rappels automatiques de rendez-vous"""
    with app.app_context():
        try:
            from utils.notifications import NotificationService, ReminderScheduler

            # Vérifier si les rappels sont activés
            if not os.environ.get('ENABLE_REMINDERS', 'False').lower() == 'true':
                logger.info("Rappels automatiques désactivés")
                return

            # Initialiser le service
            notification_service = NotificationService()

            if not notification_service.is_configured():
                logger.warning("Service de notifications non configuré")
                return

            scheduler = ReminderScheduler(notification_service)

            # Déterminer la méthode d'envoi
            method = os.environ.get('REMINDER_METHOD', 'both')

            # Envoyer les rappels
            stats = scheduler.send_all_pending_reminders(method=method)

            logger.info(f"Rappels envoyés : {stats['sent']}/{stats['total']}")
            if stats['failed'] > 0:
                logger.warning(f"Échecs : {stats['failed']}")
                for error in stats['errors']:
                    logger.error(f"Erreur pour RDV {error['appointment_id']}: {error['error']}")

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des rappels : {e}")


def sync_google_calendar(app):
    """Synchroniser avec Google Calendar"""
    with app.app_context():
        try:
            from utils.google_integration import GoogleIntegration
            from models import Appointment

            google = GoogleIntegration()

            if not google.calendar_service:
                logger.warning("Google Calendar non configuré")
                return

            # Récupérer les rendez-vous récents sans ID Google
            from datetime import datetime, timedelta
            today = datetime.now().date()

            appointments = Appointment.query.filter(
                Appointment.date >= today,
                Appointment.status == 'scheduled'
            ).all()

            synced = 0
            for appointment in appointments:
                # Vérifier si l'événement existe déjà dans Google Calendar
                # (vous pouvez ajouter un champ google_event_id au modèle Appointment)
                # Pour l'instant, on log simplement
                logger.info(f"Sync RDV {appointment.id}: {appointment.date} {appointment.time}")
                synced += 1

            logger.info(f"{synced} rendez-vous vérifiés pour la synchronisation")

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation Google Calendar : {e}")


class AppScheduler:
    """Gestionnaire de tâches planifiées"""

    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        logger.info("Scheduler démarré")

    def setup_jobs(self):
        """Configurer les tâches planifiées"""

        # Rappels de rendez-vous - tous les jours à 10h
        self.scheduler.add_job(
            func=lambda: send_automatic_reminders(self.app),
            trigger=CronTrigger(hour=10, minute=0),
            id='send_reminders',
            name='Envoi des rappels de rendez-vous',
            replace_existing=True
        )
        logger.info("Tâche planifiée : Rappels quotidiens à 10h")

        # Synchronisation Google Calendar - toutes les heures
        self.scheduler.add_job(
            func=lambda: sync_google_calendar(self.app),
            trigger=CronTrigger(minute=0),  # Toutes les heures
            id='sync_calendar',
            name='Synchronisation Google Calendar',
            replace_existing=True
        )
        logger.info("Tâche planifiée : Sync Google Calendar toutes les heures")

    def send_test_reminder(self):
        """Envoyer un rappel de test (pour debug)"""
        send_automatic_reminders(self.app)

    def shutdown(self):
        """Arrêter le scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler arrêté")
