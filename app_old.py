from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from config import Config
import os

# Initialisation de l'application
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation de la base de données
db = SQLAlchemy(app)

# Initialisation de la gestion d'authentification
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Import des modèles (après db)
from models import User, Patient, Appointment, Questionnaire, QuestionnaireResponse

# Import des routes
from routes import auth, patients, appointments, questionnaires, documents

# Enregistrement des blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(patients.bp)
app.register_blueprint(appointments.bp)
app.register_blueprint(questionnaires.bp)
app.register_blueprint(documents.bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('appointments.dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    from datetime import datetime, timedelta

    # Statistiques du jour
    today = datetime.now().date()
    today_appointments = Appointment.query.filter(
        Appointment.date == today
    ).all()

    # Rendez-vous à venir
    upcoming_appointments = Appointment.query.filter(
        Appointment.date >= today
    ).order_by(Appointment.date, Appointment.time).limit(5).all()

    # Statistiques générales
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()

    return render_template('dashboard.html',
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         total_patients=total_patients,
                         total_appointments=total_appointments)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
