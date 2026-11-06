import os
import secrets
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def _secret_key():
    """Clé secrète des sessions : celle du .env, sinon une clé aléatoire
    créée au premier lancement et conservée dans .secret_key (jamais dans Git)."""
    key = os.environ.get('SECRET_KEY')
    if key and key != 'votre_cle_secrete_a_changer':
        return key
    path = os.path.join(basedir, '.secret_key')
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(secrets.token_hex(32))
        os.chmod(path, 0o600)
    with open(path) as f:
        return f.read().strip()

class Config:
    """Configuration de base pour l'application"""

    # Clé secrète pour les sessions
    SECRET_KEY = _secret_key()
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

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
