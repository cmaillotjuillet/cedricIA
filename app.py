from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from config import Config
from extensions import db, login_manager
import os

# Initialisation de l'application
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Import des modèles (après db)
from models import User, Patient, Appointment, Questionnaire, QuestionnaireResponse

# Import des routes
from routes import auth, patients, appointments, questionnaires, documents, notifications

# Enregistrement des blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(patients.bp)
app.register_blueprint(appointments.bp)
app.register_blueprint(questionnaires.bp)
app.register_blueprint(documents.bp)
app.register_blueprint(notifications.bp)


STATUTS = {
    'scheduled': 'Prévu',
    'completed': 'Effectué',
    'cancelled': 'Annulé',
    'no_show': 'Absent',
}


@app.template_filter('statut')
def statut_filter(value):
    """Traduire le statut d'un rendez-vous en français"""
    return STATUTS.get(value, value or '')


@app.template_filter('questions_ordonnees')
def questions_ordonnees(questions):
    """Trier les questions par numéro (id) quand tous les id sont des entiers,
    pour que la numérotation corresponde à la méthode de cotation (ex. HAD)."""
    questions = list(questions or [])
    if questions and all(isinstance(q.get('id'), int) for q in questions):
        return sorted(questions, key=lambda q: q['id'])
    return questions


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    from datetime import datetime

    today = datetime.now().date()

    # Rendez-vous du jour (hors annulés), triés par heure
    today_appointments = Appointment.query.filter(
        Appointment.date == today,
        Appointment.status != 'cancelled'
    ).order_by(Appointment.time).all()

    # Rendez-vous à venir (hors annulés)
    upcoming_appointments = Appointment.query.filter(
        Appointment.date >= today,
        Appointment.status != 'cancelled'
    ).order_by(Appointment.date, Appointment.time).limit(5).all()

    # Statistiques générales
    total_patients = Patient.query.filter_by(active=True).count()
    total_appointments = Appointment.query.count()

    return render_template('dashboard.html',
                           today_appointments=today_appointments,
                           upcoming_appointments=upcoming_appointments,
                           total_patients=total_patients,
                           total_appointments=total_appointments)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Le planificateur n'est démarré qu'ici (et pas à l'import) et le
    # rechargeur automatique est désactivé : sinon deux planificateurs
    # tourneraient en parallèle et les SMS partiraient en double.
    from utils.scheduler import AppScheduler
    scheduler = AppScheduler(app)
    scheduler.setup_jobs()

    try:
        # Port 5000 souvent pris par AirPlay sur Mac : le lanceur utilise 5050
        app.run(debug=True, use_reloader=False,
                port=int(os.environ.get('PORT', 5000)))
    finally:
        scheduler.shutdown()
