from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Appointment, Patient
from extensions import db
from datetime import datetime, timedelta, date, time
import calendar as cal_module

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

MOIS_FR = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
           'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
JOURS_FR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']


def sync_google_calendar(appointment, action):
    """Synchroniser un rendez-vous avec Google Agenda.

    action : 'create', 'update' ou 'delete'.
    Ne fait rien si Google Agenda n'est pas configuré ; en cas d'erreur,
    affiche un avertissement sans interrompre l'application.
    Retourne True si la synchronisation a eu lieu.
    """
    try:
        from utils.google_integration import GoogleIntegration
        google = GoogleIntegration()
        if not google.calendar_service:
            return False

        if action == 'create':
            appointment.google_event_id = google.create_calendar_event(appointment)
        elif action == 'update':
            if appointment.google_event_id:
                google.update_calendar_event(appointment.google_event_id, appointment)
            else:
                appointment.google_event_id = google.create_calendar_event(appointment)
        elif action == 'delete':
            if appointment.google_event_id:
                google.delete_calendar_event(appointment.google_event_id)
                appointment.google_event_id = None
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Google Agenda non synchronisé : {e}', 'warning')
        return False


def _parse_time(value):
    """Accepte HH:MM ou HH:MM:SS"""
    return datetime.strptime((value or '')[:5], '%H:%M').time()


@bp.route('/dashboard')
@login_required
def dashboard():
    """Ancien tableau de bord : redirige vers le tableau de bord principal"""
    return redirect(url_for('dashboard'))


@bp.route('/calendar')
@login_required
def calendar():
    """Vue calendrier mensuelle des rendez-vous"""
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    if month < 1 or month > 12:
        month = today.month

    weeks = cal_module.Calendar(firstweekday=0).monthdatescalendar(year, month)
    grid_start = weeks[0][0]
    grid_end = weeks[-1][-1]

    appointments = Appointment.query.filter(
        Appointment.date >= grid_start,
        Appointment.date <= grid_end,
        Appointment.status != 'cancelled'
    ).order_by(Appointment.date, Appointment.time).all()

    by_day = {}
    for apt in appointments:
        by_day.setdefault(apt.date, []).append(apt)

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return render_template('appointments/calendar.html',
                           weeks=weeks,
                           by_day=by_day,
                           year=year,
                           month=month,
                           month_name=MOIS_FR[month],
                           day_names=JOURS_FR,
                           today=today,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_appointment():
    """Créer un nouveau rendez-vous"""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        try:
            appointment_date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
            appointment_time = _parse_time(request.form.get('time'))
        except ValueError:
            flash('Date ou heure invalide.', 'error')
            return redirect(url_for('appointments.new_appointment', patient_id=patient_id))

        if not patient_id or not Patient.query.get(patient_id):
            flash('Veuillez choisir un patient.', 'error')
            return redirect(url_for('appointments.new_appointment',
                                    date=appointment_date.isoformat()))

        # Vérifier la disponibilité
        existing = Appointment.query.filter(
            Appointment.date == appointment_date,
            Appointment.time == appointment_time,
            Appointment.status != 'cancelled'
        ).first()

        if existing:
            flash('Ce créneau est déjà réservé.', 'error')
            return redirect(url_for('appointments.new_appointment',
                                    patient_id=patient_id,
                                    date=appointment_date.isoformat()))

        appointment = Appointment(
            patient_id=patient_id,
            date=appointment_date,
            time=appointment_time,
            duration=request.form.get('duration', 60, type=int) or 60,
            appointment_type=request.form.get('appointment_type'),
            therapy_type=request.form.get('therapy_type'),
            notes=request.form.get('notes')
        )

        db.session.add(appointment)
        db.session.commit()

        if sync_google_calendar(appointment, 'create'):
            flash('Rendez-vous créé et ajouté à Google Agenda !', 'success')
        else:
            flash('Rendez-vous créé avec succès !', 'success')

        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))

    patients = Patient.query.filter_by(active=True).order_by(Patient.last_name, Patient.first_name).all()
    return render_template('appointments/new.html',
                           patients=patients,
                           selected_patient_id=request.args.get('patient_id', type=int),
                           selected_date=request.args.get('date', ''))


@bp.route('/<int:appointment_id>')
@login_required
def view_appointment(appointment_id):
    """Voir les détails d'un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('appointments/view.html', appointment=appointment)


@bp.route('/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    """Modifier un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        try:
            new_date = datetime.strptime(request.form.get('date', ''), '%Y-%m-%d').date()
            new_time = _parse_time(request.form.get('time'))
        except ValueError:
            flash('Date ou heure invalide.', 'error')
            return redirect(url_for('appointments.edit_appointment', appointment_id=appointment.id))

        # Nouveau créneau : un nouveau rappel devra être envoyé
        if new_date != appointment.date or new_time != appointment.time:
            appointment.reminder_sent = False

        appointment.patient_id = request.form.get('patient_id', appointment.patient_id, type=int)
        appointment.date = new_date
        appointment.time = new_time
        appointment.duration = request.form.get('duration', 60, type=int) or 60
        appointment.appointment_type = request.form.get('appointment_type')
        appointment.therapy_type = request.form.get('therapy_type')
        appointment.status = request.form.get('status') or appointment.status
        appointment.notes = request.form.get('notes')

        db.session.commit()

        if appointment.status == 'cancelled':
            sync_google_calendar(appointment, 'delete')
        elif appointment.google_event_id:
            sync_google_calendar(appointment, 'update')
        else:
            sync_google_calendar(appointment, 'create')

        flash('Rendez-vous modifié avec succès !', 'success')
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))

    patients = Patient.query.filter_by(active=True).order_by(Patient.last_name, Patient.first_name).all()
    return render_template('appointments/edit.html', appointment=appointment, patients=patients)


@bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Annuler un rendez-vous"""
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()

    sync_google_calendar(appointment, 'delete')

    flash('Rendez-vous annulé.', 'info')
    return redirect(url_for('dashboard'))


@bp.route('/available-slots')
@login_required
def available_slots():
    """API pour obtenir les créneaux disponibles"""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date requise'}), 400

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Date invalide'}), 400

    # Heures d'ouverture par défaut (9h-18h)
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    slot_duration = 60  # minutes

    all_slots = []
    current_time = datetime.combine(selected_date, opening_time)
    end_time = datetime.combine(selected_date, closing_time)

    while current_time < end_time:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=slot_duration)

    existing_appointments = Appointment.query.filter(
        Appointment.date == selected_date,
        Appointment.status != 'cancelled'
    ).all()

    booked_slots = [apt.time for apt in existing_appointments]
    available = [slot.strftime('%H:%M') for slot in all_slots if slot not in booked_slots]

    return jsonify({'available_slots': available})
