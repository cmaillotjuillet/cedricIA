from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Modèle pour le thérapeute/utilisateur"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    specialties = db.Column(db.String(500))  # TCC, ACT, Sophrologie, Hypnose
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Patient(db.Model):
    """Modèle pour les patients"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(300))

    # Informations médicales
    medical_history = db.Column(db.Text)
    current_treatments = db.Column(db.Text)
    allergies = db.Column(db.Text)
    emergency_contact = db.Column(db.String(200))

    # Informations thérapeutiques
    therapy_type = db.Column(db.String(100))  # TCC, ACT, Sophrologie, etc.
    first_session_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    # Relations
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('TherapySession', backref='patient', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'


class Appointment(db.Model):
    """Modèle pour les rendez-vous"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=60)  # durée en minutes
    appointment_type = db.Column(db.String(100))  # Première consultation, Suivi, etc.
    therapy_type = db.Column(db.String(100))  # TCC, ACT, Sophrologie, Hypnose
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no_show
    notes = db.Column(db.Text)
    reminder_sent = db.Column(db.Boolean, default=False)
    google_event_id = db.Column(db.String(200))  # ID de l'événement Google Calendar

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.date} {self.time} - Patient {self.patient_id}>'


class TherapySession(db.Model):
    """Modèle pour les séances de thérapie (notes détaillées)"""
    __tablename__ = 'therapy_sessions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    session_date = db.Column(db.DateTime, nullable=False)
    session_number = db.Column(db.Integer)

    # Contenu de la séance
    therapy_type = db.Column(db.String(100))
    objectives = db.Column(db.Text)
    interventions = db.Column(db.Text)
    patient_progress = db.Column(db.Text)
    homework = db.Column(db.Text)  # Exercices à faire
    next_session_plan = db.Column(db.Text)

    # Évaluations
    mood_score = db.Column(db.Integer)  # 1-10
    anxiety_score = db.Column(db.Integer)  # 1-10

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TherapySession {self.session_date} - Patient {self.patient_id}>'


class Questionnaire(db.Model):
    """Modèle pour les questionnaires thérapeutiques"""
    __tablename__ = 'questionnaires'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(50))  # HAD, Beck, etc.
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # Anxiété, Dépression, etc.
    questions = db.Column(db.JSON)  # Liste des questions au format JSON
    scoring_method = db.Column(db.Text)  # Instructions de cotation
    interpretation = db.Column(db.Text)  # Guide d'interprétation

    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    responses = db.relationship('QuestionnaireResponse', backref='questionnaire', lazy='dynamic')

    def __repr__(self):
        return f'<Questionnaire {self.name}>'


class QuestionnaireResponse(db.Model):
    """Modèle pour les réponses aux questionnaires"""
    __tablename__ = 'questionnaire_responses'

    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('therapy_sessions.id'))

    responses = db.Column(db.JSON)  # Réponses au format JSON
    total_score = db.Column(db.Float)
    interpretation = db.Column(db.Text)

    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<QuestionnaireResponse {self.questionnaire_id} - Patient {self.patient_id}>'


class Document(db.Model):
    """Modèle pour les documents générés"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    document_type = db.Column(db.String(100))  # Compte-rendu, Ordonnance, etc.
    title = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    google_doc_id = db.Column(db.String(200))  # ID du document Google Docs si intégré

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.title}>'
