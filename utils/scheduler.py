"""
Scheduler pour les tâches automatiques
- Envoi de rappels de rendez-vous
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


class AppScheduler:
    """Gestionnaire de tâches planifiées"""

    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        logger.info("Scheduler démarré")

    def setup_jobs(self):
        """Configurer les tâches planifiées"""

        # Rappels : vérification toutes les heures de 8h à 20h.
        # Chaque RDV reçoit un rappel unique environ REMINDER_HOURS_BEFORE
        # heures avant (reminder_sent évite les doublons).
        self.scheduler.add_job(
            func=lambda: send_automatic_reminders(self.app),
            trigger=CronTrigger(hour='8-20', minute=0),
            id='send_reminders',
            name='Envoi des rappels de rendez-vous',
            replace_existing=True
        )
        logger.info("Tâche planifiée : vérification des rappels toutes les heures de 8h à 20h")

    def send_test_reminder(self):
        """Envoyer un rappel de test (pour debug)"""
        send_automatic_reminders(self.app)

    def shutdown(self):
        """Arrêter le scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler arrêté")
