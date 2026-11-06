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
    patients = Patient.query.filter_by(active=True).order_by(Patient.last_name, Patient.first_name).all()
    return render_template('questionnaires/view.html', questionnaire=questionnaire, patients=patients)

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
    details, subscores = build_response_details(response)
    return render_template('questionnaires/response.html',
                           response=response,
                           details=details,
                           subscores=subscores)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_questionnaire():
    """Créer un nouveau questionnaire"""
    if request.method == 'POST':
        # Récupérer les questions au format JSON
        questions_data = request.form.get('questions_json')
        import json
        try:
            questions = json.loads(questions_data) if questions_data else []
            if not isinstance(questions, list):
                raise ValueError('une liste [...] est attendue')
        except ValueError as e:
            flash(f'Format JSON des questions invalide : {e}', 'error')
            return render_template('questionnaires/new.html', form=request.form)

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

    return render_template('questionnaires/new.html', form={})

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


SUBSCALE_LABELS = {
    'anxiety': 'Anxiété',
    'depression': 'Dépression',
}


def build_response_details(response):
    """Retrouver le libellé de chaque réponse et calculer les sous-scores.

    Retourne (details, subscores) :
    - details : liste de dicts {number, text, answer, score}
    - subscores : liste de (libellé, score) par sous-échelle, dans l'ordre
      d'apparition des questions
    """
    answers = response.responses or {}
    questions = list(response.questionnaire.questions or [])
    if questions and all(isinstance(q.get('id'), int) for q in questions):
        questions.sort(key=lambda q: q['id'])
    details = []
    subscores = {}

    for idx, question in enumerate(questions, 1):
        qid = str(question.get('id', idx))
        raw = answers.get(qid)
        options = question.get('options') or []
        scores = question.get('scores') or list(range(len(options)))
        label = None
        score = None

        if raw not in (None, ''):
            try:
                score = float(raw)
            except (TypeError, ValueError):
                score = None
            if score is not None:
                for opt, sc in zip(options, scores):
                    try:
                        if float(sc) == score:
                            label = opt
                            break
                    except (TypeError, ValueError):
                        continue
            if label is None:
                label = str(raw)

        subscale = question.get('subscale')
        if subscale:
            key = SUBSCALE_LABELS.get(subscale, subscale.capitalize())
            subscores.setdefault(key, 0)
            if score is not None:
                subscores[key] += score

        details.append({
            'number': question.get('id', idx),
            'text': question.get('text', 'Question {}'.format(idx)),
            'answer': label,
            'score': score,
        })

    return details, list(subscores.items())
