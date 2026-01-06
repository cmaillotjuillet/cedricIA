import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuration de base pour l'application"""

    # Clé secrète pour les sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'cabinet.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration Google API
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')

    # Dossiers de stockage
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    PDF_FOLDER = os.path.join(basedir, 'generated_pdfs')

    # Configuration de pagination
    ITEMS_PER_PAGE = 20

    # Fuseau horaire
    TIMEZONE = 'Europe/Paris'
