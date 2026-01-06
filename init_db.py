"""
Script pour initialiser la base de données
avec les tables et les questionnaires pré-définis
"""

from app import app
from extensions import db
from models import User, Questionnaire
from utils.predefined_questionnaires import get_predefined_questionnaires

def init_database():
    """Initialiser la base de données"""
    with app.app_context():
        # Créer toutes les tables
        print("Création des tables...")
        db.create_all()
        print("✓ Tables créées")

        # Vérifier s'il y a déjà des questionnaires
        existing_questionnaires = Questionnaire.query.count()

        if existing_questionnaires == 0:
            print("\nAjout des questionnaires pré-définis...")
            questionnaires = get_predefined_questionnaires()

            for q_data in questionnaires:
                questionnaire = Questionnaire(
                    name=q_data['name'],
                    short_name=q_data['short_name'],
                    description=q_data['description'],
                    category=q_data['category'],
                    questions=q_data['questions'],
                    scoring_method=q_data['scoring_method'],
                    interpretation=q_data['interpretation'],
                    active=True
                )
                db.session.add(questionnaire)
                print(f"  ✓ {q_data['short_name']}: {q_data['name']}")

            db.session.commit()
            print("\n✓ Questionnaires ajoutés avec succès")
        else:
            print(f"\n✓ {existing_questionnaires} questionnaire(s) déjà présent(s)")

        # Vérifier s'il y a déjà un utilisateur
        existing_users = User.query.count()

        if existing_users == 0:
            print("\n" + "="*60)
            print("PREMIER LANCEMENT")
            print("="*60)
            print("\nAucun utilisateur trouvé.")
            print("Veuillez créer un compte en vous rendant sur:")
            print("  http://localhost:5000/auth/register")
            print("\nOu démarrez l'application avec:")
            print("  python app.py")
            print("="*60)
        else:
            print(f"\n✓ {existing_users} utilisateur(s) enregistré(s)")

        print("\n✓ Base de données initialisée avec succès !")
        print("\nVous pouvez maintenant démarrer l'application avec:")
        print("  python app.py")

if __name__ == '__main__':
    init_database()
