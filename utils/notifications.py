"""
Système de notifications pour les rappels de rendez-vous
Supporte SMS et WhatsApp via Twilio
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from datetime import datetime


class NotificationService:
    """Service de notifications SMS et WhatsApp"""

    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        self.whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"Erreur lors de l'initialisation de Twilio: {e}")

    def is_configured(self):
        """Vérifier si Twilio est configuré"""
        return self.client is not None

    def send_sms(self, to_phone, message):
        """Envoyer un SMS"""
        if not self.is_configured():
            raise Exception("Twilio n'est pas configuré. Vérifiez vos variables d'environnement.")

        if not self.phone_number:
            raise Exception("Numéro de téléphone Twilio non configuré (TWILIO_PHONE_NUMBER)")

        try:
            # Normaliser le numéro (ajouter +33 si nécessaire)
            to_phone = self._normalize_phone(to_phone)

            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )

            return {
                'success': True,
                'sid': message_obj.sid,
                'status': message_obj.status
            }

        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'code': e.code
            }

    def send_whatsapp(self, to_phone, message):
        """Envoyer un message WhatsApp"""
        if not self.is_configured():
            raise Exception("Twilio n'est pas configuré. Vérifiez vos variables d'environnement.")

        if not self.whatsapp_number:
            raise Exception("Numéro WhatsApp Twilio non configuré (TWILIO_WHATSAPP_NUMBER)")

        try:
            # Normaliser le numéro
            to_phone = self._normalize_phone(to_phone)

            # Format WhatsApp : whatsapp:+33...
            to_whatsapp = f"whatsapp:{to_phone}"

            message_obj = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_whatsapp
            )

            return {
                'success': True,
                'sid': message_obj.sid,
                'status': message_obj.status
            }

        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e),
                'code': e.code
            }

    def send_appointment_reminder(self, appointment, method='both'):
        """
        Envoyer un rappel de rendez-vous

        Args:
            appointment: L'objet Appointment
            method: 'sms', 'whatsapp' ou 'both'

        Returns:
            dict avec les résultats
        """
        patient = appointment.patient

        if not patient.phone:
            return {
                'success': False,
                'error': 'Patient sans numéro de téléphone'
            }

        # Formater le message
        message = self._format_appointment_message(appointment)

        results = {
            'sms': None,
            'whatsapp': None
        }

        # Envoyer SMS
        if method in ['sms', 'both']:
            try:
                results['sms'] = self.send_sms(patient.phone, message)
            except Exception as e:
                results['sms'] = {'success': False, 'error': str(e)}

        # Envoyer WhatsApp
        if method in ['whatsapp', 'both']:
            try:
                results['whatsapp'] = self.send_whatsapp(patient.phone, message)
            except Exception as e:
                results['whatsapp'] = {'success': False, 'error': str(e)}

        # Déterminer le succès global
        success = False
        if method == 'both':
            success = (results['sms'] and results['sms'].get('success')) or \
                     (results['whatsapp'] and results['whatsapp'].get('success'))
        elif method == 'sms':
            success = results['sms'] and results['sms'].get('success', False)
        elif method == 'whatsapp':
            success = results['whatsapp'] and results['whatsapp'].get('success', False)

        return {
            'success': success,
            'results': results,
            'method': method
        }

    def _format_appointment_message(self, appointment):
        """Formater le message de rappel de rendez-vous"""
        patient = appointment.patient
        date_str = appointment.date.strftime('%d/%m/%Y')
        time_str = appointment.time.strftime('%H:%M')

        message = f"""Bonjour {patient.first_name},

Rappel de votre rendez-vous :
📅 Date : {date_str}
⏰ Heure : {time_str}
⏱ Durée : {appointment.duration} minutes
💼 Type : {appointment.therapy_type or 'Consultation'}

En cas d'empêchement, merci de prévenir le plus tôt possible.

À bientôt !"""

        return message

    def _normalize_phone(self, phone):
        """Normaliser un numéro de téléphone au format international"""
        # Retirer tous les espaces et caractères spéciaux
        phone = phone.replace(' ', '').replace('.', '').replace('-', '')

        # Si le numéro commence par 0, remplacer par +33
        if phone.startswith('0'):
            phone = '+33' + phone[1:]

        # Si le numéro ne commence pas par +, ajouter +33
        if not phone.startswith('+'):
            phone = '+33' + phone

        return phone

    def send_test_message(self, to_phone, method='sms'):
        """Envoyer un message de test"""
        test_message = """Test de notification CedricIA

Ce message confirme que votre système de notifications fonctionne correctement.

✅ Configuration réussie !"""

        if method == 'sms':
            return self.send_sms(to_phone, test_message)
        elif method == 'whatsapp':
            return self.send_whatsapp(to_phone, test_message)
        else:
            return {
                'success': False,
                'error': 'Méthode invalide. Utilisez "sms" ou "whatsapp"'
            }


class ReminderScheduler:
    """Gestion des rappels automatiques"""

    def __init__(self, notification_service):
        self.notification_service = notification_service

    def get_appointments_needing_reminder(self, hours_before=24):
        """
        Récupérer les rendez-vous qui nécessitent un rappel

        Args:
            hours_before: Nombre d'heures avant le RDV pour envoyer le rappel

        Returns:
            Liste d'objets Appointment
        """
        from models import Appointment
        from datetime import datetime, timedelta

        # Calculer la plage de temps
        now = datetime.now()
        target_start = now + timedelta(hours=hours_before - 1)
        target_end = now + timedelta(hours=hours_before + 1)

        # Récupérer les rendez-vous
        appointments = Appointment.query.filter(
            Appointment.status == 'scheduled',
            Appointment.reminder_sent == False,
            Appointment.date >= target_start.date(),
            Appointment.date <= target_end.date()
        ).all()

        # Filtrer par heure
        appointments_to_remind = []
        for apt in appointments:
            apt_datetime = datetime.combine(apt.date, apt.time)
            time_diff = (apt_datetime - now).total_seconds() / 3600

            # Si dans la fenêtre de rappel (hours_before ± 1 heure)
            if hours_before - 1 <= time_diff <= hours_before + 1:
                appointments_to_remind.append(apt)

        return appointments_to_remind

    def send_all_pending_reminders(self, method='both'):
        """
        Envoyer tous les rappels en attente

        Args:
            method: 'sms', 'whatsapp' ou 'both'

        Returns:
            dict avec statistiques
        """
        from extensions import db

        hours_before = int(os.environ.get('REMINDER_HOURS_BEFORE', 24))
        appointments = self.get_appointments_needing_reminder(hours_before)

        stats = {
            'total': len(appointments),
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        for appointment in appointments:
            try:
                result = self.notification_service.send_appointment_reminder(
                    appointment,
                    method=method
                )

                if result['success']:
                    # Marquer comme envoyé
                    appointment.reminder_sent = True
                    db.session.commit()
                    stats['sent'] += 1
                else:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'appointment_id': appointment.id,
                        'patient': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                        'error': result.get('results', {})
                    })

            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append({
                    'appointment_id': appointment.id,
                    'patient': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                    'error': str(e)
                })

        return stats
