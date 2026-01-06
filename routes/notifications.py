from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Appointment, Patient
from extensions import db
from utils.notifications import NotificationService, ReminderScheduler
from datetime import datetime

bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@bp.route('/settings')
@login_required
def settings():
    """Page de configuration des notifications"""
    import os

    config = {
        'twilio_configured': bool(os.environ.get('TWILIO_ACCOUNT_SID')),
        'enable_reminders': os.environ.get('ENABLE_REMINDERS', 'False').lower() == 'true',
        'reminder_hours_before': os.environ.get('REMINDER_HOURS_BEFORE', '24'),
        'reminder_method': os.environ.get('REMINDER_METHOD', 'both')
    }

    return render_template('notifications/settings.html', config=config)

@bp.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    """Tester l'envoi de notifications"""
    if request.method == 'POST':
        phone = request.form.get('phone')
        method = request.form.get('method', 'sms')

        notification_service = NotificationService()

        if not notification_service.is_configured():
            flash('Twilio n\'est pas configuré. Vérifiez vos variables d\'environnement.', 'error')
            return redirect(url_for('notifications.test'))

        try:
            result = notification_service.send_test_message(phone, method=method)

            if result['success']:
                flash(f'Message de test envoyé avec succès ! SID: {result["sid"]}', 'success')
            else:
                flash(f'Erreur lors de l\'envoi: {result.get("error")}', 'error')

        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')

        return redirect(url_for('notifications.test'))

    return render_template('notifications/test.html')

@bp.route('/send-reminder/<int:appointment_id>', methods=['POST'])
@login_required
def send_reminder(appointment_id):
    """Envoyer un rappel manuel pour un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)

    method = request.form.get('method', 'both')

    notification_service = NotificationService()

    if not notification_service.is_configured():
        flash('Service de notifications non configuré', 'error')
        return redirect(request.referrer or url_for('appointments.dashboard'))

    try:
        result = notification_service.send_appointment_reminder(appointment, method=method)

        if result['success']:
            appointment.reminder_sent = True
            db.session.commit()
            flash('Rappel envoyé avec succès !', 'success')
        else:
            errors = result.get('results', {})
            flash(f'Erreur lors de l\'envoi du rappel: {errors}', 'error')

    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')

    return redirect(request.referrer or url_for('appointments.view_appointment', appointment_id=appointment_id))

@bp.route('/send-all-reminders', methods=['POST'])
@login_required
def send_all_reminders():
    """Envoyer tous les rappels en attente (manuel)"""
    method = request.form.get('method', 'both')

    notification_service = NotificationService()

    if not notification_service.is_configured():
        return jsonify({
            'success': False,
            'error': 'Service non configuré'
        }), 400

    try:
        scheduler = ReminderScheduler(notification_service)
        stats = scheduler.send_all_pending_reminders(method=method)

        flash(f'Rappels envoyés : {stats["sent"]}/{stats["total"]}. Échecs : {stats["failed"]}', 'success' if stats['failed'] == 0 else 'warning')

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/pending-reminders')
@login_required
def pending_reminders():
    """Liste des rendez-vous en attente de rappel"""
    notification_service = NotificationService()
    scheduler = ReminderScheduler(notification_service)

    hours_before = int(request.args.get('hours', 24))
    appointments = scheduler.get_appointments_needing_reminder(hours_before=hours_before)

    return render_template('notifications/pending.html',
                         appointments=appointments,
                         hours_before=hours_before)

@bp.route('/history')
@login_required
def history():
    """Historique des rappels envoyés"""
    # Rendez-vous avec rappels envoyés
    sent_reminders = Appointment.query.filter(
        Appointment.reminder_sent == True
    ).order_by(db.desc(Appointment.date)).limit(50).all()

    return render_template('notifications/history.html',
                         sent_reminders=sent_reminders)
