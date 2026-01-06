from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Appointment, Patient
from extensions import db
from datetime import datetime, timedelta, date, time

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord des rendez-vous"""
    today = date.today()

    # Rendez-vous d'aujourd'hui
    today_appointments = Appointment.query.filter(
        Appointment.date == today
    ).order_by(Appointment.time).all()

    # Rendez-vous de la semaine
    week_start = today
    week_end = today + timedelta(days=7)
    week_appointments = Appointment.query.filter(
        Appointment.date.between(week_start, week_end)
    ).order_by(Appointment.date, Appointment.time).all()

    return render_template('appointments/dashboard.html',
                         today_appointments=today_appointments,
                         week_appointments=week_appointments,
                         today=today)

@bp.route('/calendar')
@login_required
def calendar():
    """Vue calendrier des rendez-vous"""
    # Récupérer le mois à afficher
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Récupérer les rendez-vous du mois
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    appointments = Appointment.query.filter(
        Appointment.date >= start_date,
        Appointment.date < end_date
    ).order_by(Appointment.date, Appointment.time).all()

    return render_template('appointments/calendar.html',
                         appointments=appointments,
                         year=year,
                         month=month)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_appointment():
    """Créer un nouveau rendez-vous"""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        appointment_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        appointment_time = datetime.strptime(request.form.get('time'), '%H:%M').time()

        # Vérifier la disponibilité
        existing = Appointment.query.filter(
            Appointment.date == appointment_date,
            Appointment.time == appointment_time,
            Appointment.status != 'cancelled'
        ).first()

        if existing:
            flash('Ce créneau est déjà réservé.', 'error')
            return redirect(request.url)

        appointment = Appointment(
            patient_id=patient_id,
            date=appointment_date,
            time=appointment_time,
            duration=int(request.form.get('duration', 60)),
            appointment_type=request.form.get('appointment_type'),
            therapy_type=request.form.get('therapy_type'),
            notes=request.form.get('notes')
        )

        db.session.add(appointment)
        db.session.commit()

        # Ajouter à Google Calendar si configuré
        try:
            from utils.google_integration import GoogleIntegration
            google = GoogleIntegration()
            if google.calendar_service:
                event_id = google.create_calendar_event(appointment)
                appointment.google_event_id = event_id
                db.session.commit()
                flash('Rendez-vous créé et ajouté à Google Agenda !', 'success')
            else:
                flash('Rendez-vous créé avec succès !', 'success')
        except Exception as e:
            flash('Rendez-vous créé (erreur Google Agenda)', 'warning')

        return redirect(url_for('appointments.dashboard'))

    # Liste des patients pour le formulaire
    patients = Patient.query.filter_by(active=True).order_by(Patient.last_name, Patient.first_name).all()

    return render_template('appointments/new.html', patients=patients)

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
        appointment.patient_id = request.form.get('patient_id')
        appointment.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        appointment.time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        appointment.duration = int(request.form.get('duration', 60))
        appointment.appointment_type = request.form.get('appointment_type')
        appointment.therapy_type = request.form.get('therapy_type')
        appointment.status = request.form.get('status')
        appointment.notes = request.form.get('notes')

        db.session.commit()
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

    flash('Rendez-vous annulé.', 'info')
    return redirect(url_for('appointments.dashboard'))

@bp.route('/available-slots')
@login_required
def available_slots():
    """API pour obtenir les créneaux disponibles"""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date requise'}), 400

    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Heures d'ouverture par défaut (9h-18h)
    opening_time = time(9, 0)
    closing_time = time(18, 0)
    slot_duration = 60  # minutes

    # Générer tous les créneaux possibles
    all_slots = []
    current_time = datetime.combine(selected_date, opening_time)
    end_time = datetime.combine(selected_date, closing_time)

    while current_time < end_time:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=slot_duration)

    # Récupérer les rendez-vous existants
    existing_appointments = Appointment.query.filter(
        Appointment.date == selected_date,
        Appointment.status != 'cancelled'
    ).all()

    booked_slots = [apt.time for apt in existing_appointments]

    # Créneaux disponibles
    available = [slot.strftime('%H:%M') for slot in all_slots if slot not in booked_slots]

    return jsonify({'available_slots': available})
