from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Patient, Appointment, TherapySession, QuestionnaireResponse, Questionnaire
from extensions import db
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')


def _parse_date(value):
    """Convertir 'AAAA-MM-JJ' en date ; vide ou invalide -> None"""
    try:
        return datetime.strptime(value, '%Y-%m-%d').date() if value else None
    except ValueError:
        return None


@bp.route('/')
@login_required
def list_patients():
    """Liste des patients"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Patient.query.filter_by(active=True)

    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.email.ilike(f'%{search}%')
            )
        )

    patients = query.order_by(Patient.last_name, Patient.first_name).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('patients/list.html', patients=patients, search=search)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_patient():
    """Créer un nouveau patient"""
    if request.method == 'POST':
        patient = Patient(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            date_of_birth=_parse_date(request.form.get('date_of_birth')),
            address=request.form.get('address'),
            medical_history=request.form.get('medical_history'),
            current_treatments=request.form.get('current_treatments'),
            allergies=request.form.get('allergies'),
            emergency_contact=request.form.get('emergency_contact'),
            therapy_type=request.form.get('therapy_type'),
            first_session_date=_parse_date(request.form.get('first_session_date')),
            notes=request.form.get('notes')
        )

        db.session.add(patient)
        db.session.commit()

        flash('Patient ajouté avec succès !', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.id))

    return render_template('patients/new.html')

@bp.route('/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """Voir le dossier d'un patient"""
    patient = Patient.query.get_or_404(patient_id)

    # Récupérer les rendez-vous
    appointments = patient.appointments.order_by(
        Appointment.date.desc(), Appointment.time.desc()).limit(10).all()

    # Récupérer les séances
    sessions = patient.sessions.order_by(TherapySession.session_date.desc()).limit(10).all()

    # Récupérer les questionnaires
    questionnaires = patient.questionnaire_responses.order_by(
        QuestionnaireResponse.completed_at.desc()).limit(5).all()

    # Questionnaires disponibles pour une passation immédiate
    available_questionnaires = Questionnaire.query.filter_by(active=True).order_by(Questionnaire.name).all()

    return render_template('patients/view.html',
                         patient=patient,
                         appointments=appointments,
                         sessions=sessions,
                         questionnaires=questionnaires,
                         available_questionnaires=available_questionnaires)

@bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Modifier un patient"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.email = request.form.get('email')
        patient.phone = request.form.get('phone')

        # Champ vide = date effacée
        patient.date_of_birth = _parse_date(request.form.get('date_of_birth'))

        patient.address = request.form.get('address')
        patient.medical_history = request.form.get('medical_history')
        patient.current_treatments = request.form.get('current_treatments')
        patient.allergies = request.form.get('allergies')
        patient.emergency_contact = request.form.get('emergency_contact')
        patient.therapy_type = request.form.get('therapy_type')
        patient.first_session_date = _parse_date(request.form.get('first_session_date'))
        patient.notes = request.form.get('notes')

        db.session.commit()
        flash('Patient modifié avec succès !', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.id))

    return render_template('patients/edit.html', patient=patient)

@bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """Archiver un patient"""
    patient = Patient.query.get_or_404(patient_id)
    patient.active = False
    db.session.commit()

    flash('Patient archivé avec succès.', 'info')
    return redirect(url_for('patients.list_patients'))
