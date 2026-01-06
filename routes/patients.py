from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Patient
from extensions import db
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')

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
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            address=request.form.get('address'),
            medical_history=request.form.get('medical_history'),
            current_treatments=request.form.get('current_treatments'),
            allergies=request.form.get('allergies'),
            emergency_contact=request.form.get('emergency_contact'),
            therapy_type=request.form.get('therapy_type'),
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
    appointments = patient.appointments.order_by(db.desc('date')).limit(10).all()

    # Récupérer les séances
    sessions = patient.sessions.order_by(db.desc('session_date')).limit(10).all()

    # Récupérer les questionnaires
    questionnaires = patient.questionnaire_responses.order_by(db.desc('completed_at')).limit(5).all()

    return render_template('patients/view.html',
                         patient=patient,
                         appointments=appointments,
                         sessions=sessions,
                         questionnaires=questionnaires)

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

        if request.form.get('date_of_birth'):
            patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()

        patient.address = request.form.get('address')
        patient.medical_history = request.form.get('medical_history')
        patient.current_treatments = request.form.get('current_treatments')
        patient.allergies = request.form.get('allergies')
        patient.emergency_contact = request.form.get('emergency_contact')
        patient.therapy_type = request.form.get('therapy_type')
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
