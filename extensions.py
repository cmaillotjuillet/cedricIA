"""
Extensions Flask
Séparation des extensions pour éviter les importations circulaires
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
