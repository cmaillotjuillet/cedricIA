from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import Questionnaire, QuestionnaireResponse, Patient, TherapySession
from extensions import db
from datetime import datetime

bp = Blueprint('questionnaires', __name__, url_prefix='/questionnaires')

@bp.route('/')
@login_required
def list_questionnaires():
    """Liste des questionnaires disponibles"""
    questionnaires = Questionnaire.query.filter_by(active=True).all()
    return render_template('questionnaires/list.html', questionnaires=questionnaires)

@bp.route('/<int:questionnaire_id>')
@login_required
def view_questionnaire(questionnaire_id):
    """Voir un questionnaire"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    return render_template('questionnaires/view.html', questionnaire=questionnaire)

@bp.route('/<int:questionnaire_id>/administer/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def administer_questionnaire(questionnaire_id, patient_id):
    """Faire passer un questionnaire à un patient"""
    questionnaire = Questionnaire.query.get_or_404(questionnaire_id)
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        # Récupérer les réponses
        responses = {}
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                responses[question_id] = value

        # Calculer le score si applicable
        total_score = calculate_score(questionnaire, responses)

        # Créer la réponse
        response = QuestionnaireResponse(
            questionnaire_id=questionnaire_id,
            patient_id=patient_id,
            responses=responses,
            total_score=total_score,
            notes=request.form.get('notes')
        )

        db.session.add(response)
        db.session.commit()

        flash('Questionnaire complété avec succès !', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient_id))

    return render_template('questionnaires/administer.html',
                         questionnaire=questionnaire,
                         patient=patient)

@bp.route('/response/<int:response_id>')
@login_required
def view_response(response_id):
    """Voir les réponses à un questionnaire"""
    response = QuestionnaireResponse.query.get_or_404(response_id)
    return render_template('questionnaires/response.html', response=response)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_questionnaire():
    """Créer un nouveau questionnaire"""
    if request.method == 'POST':
        # Récupérer les questions au format JSON
        questions_data = request.form.get('questions_json')
        import json
        questions = json.loads(questions_data) if questions_data else []

        questionnaire = Questionnaire(
            name=request.form.get('name'),
            short_name=request.form.get('short_name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            questions=questions,
            scoring_method=request.form.get('scoring_method'),
            interpretation=request.form.get('interpretation')
        )

        db.session.add(questionnaire)
        db.session.commit()

        flash('Questionnaire créé avec succès !', 'success')
        return redirect(url_for('questionnaires.list_questionnaires'))

    return render_template('questionnaires/new.html')

def calculate_score(questionnaire, responses):
    """Calculer le score d'un questionnaire"""
    # Logique de base - à adapter selon le type de questionnaire
    total = 0

    if not questionnaire.questions:
        return 0

    for question in questionnaire.questions:
        question_id = str(question.get('id', ''))
        if question_id in responses:
            try:
                total += float(responses[question_id])
            except (ValueError, TypeError):
                pass

    return total
