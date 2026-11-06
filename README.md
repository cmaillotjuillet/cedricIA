# CedricIA - Système de Gestion de Cabinet de Psychothérapie

Application web complète pour la gestion d'un cabinet de psychothérapie, neuropsychologie, TCC, ACT, sophrologie et hypnose.

## Fonctionnalités

### 🗓️ Gestion des rendez-vous
- Calendrier intégré avec vue mensuelle et quotidienne
- Création, modification et annulation de rendez-vous
- Détection automatique des conflits d'horaires
- Remplace Calendly avec toutes les fonctionnalités essentielles

### 👥 Gestion des patients
- Dossiers patients complets avec informations médicales
- Historique des séances
- Notes thérapeutiques détaillées
- Archivage des patients inactifs

### 📋 Questionnaires thérapeutiques
- **Questionnaires pré-définis inclus** :
  - HAD (Hospital Anxiety and Depression Scale)
  - BDI-II (Beck Depression Inventory)
  - AAQ-II (Acceptance and Action Questionnaire) pour ACT
  - MAAS (Mindful Attention Awareness Scale)
  - Questionnaire de suivi thérapeutique
- Création de questionnaires personnalisés
- Passation en direct
- Calcul automatique des scores
- Historique et évolution

### 📄 Génération de documents PDF (format A4)
- Comptes-rendus de séances
- Rapports de questionnaires
- Dossiers patients complets
- Documents imprimables professionnels

### 🔗 Intégration Google Workspace
- Export vers Google Docs
- Création automatique de feuilles de calcul (Google Sheets)
- Suivi de l'évolution des patients
- Synchronisation optionnelle

### 📅 Synchronisation Google Calendar
- **Synchronisation automatique bidirectionnelle**
- Chaque rendez-vous créé est automatiquement ajouté à votre Google Agenda
- Modification et suppression synchronisées
- Rappels Google Calendar intégrés (24h et 1h avant)
- Accès à vos rendez-vous depuis n'importe quel appareil

### 📱 Rappels automatiques SMS & WhatsApp
- **Rappels automatiques quotidiens** envoyés 24h avant les rendez-vous
- Support SMS et WhatsApp via Twilio
- Messages personnalisés avec nom du patient, date, heure et type de séance
- Envoi automatique : vérification toutes les heures de 8h à 20h, un rappel unique par RDV environ 24h avant
- Rappels manuels possibles depuis l'interface
- **WhatsApp 16x moins cher que les SMS !**
- Interface de test pour vérifier la configuration
- Historique des rappels envoyés

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
```bash
cd cedricIA
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv

# Sur Windows :
venv\Scripts\activate

# Sur macOS/Linux :
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration initiale**

Copier le fichier d'exemple de configuration :
```bash
cp .env.example .env
```

Éditer le fichier `.env` et modifier au minimum :
```
SECRET_KEY=votre_cle_secrete_unique_et_longue
```

5. **Initialiser la base de données**
```bash
python init_db.py
```

Cette commande va :
- Créer toutes les tables nécessaires
- Charger les questionnaires pré-définis (HAD, Beck, AAQ-II, MAAS, etc.)
- Préparer l'application pour le premier démarrage

6. **Démarrer l'application**
```bash
python app.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

## Premier démarrage

1. **Créer votre compte**
   - Accédez à http://localhost:5000
   - Cliquez sur "Créer un compte"
   - Remplissez vos informations (nom, email, spécialités)
   - Créez votre mot de passe

2. **Connexion**
   - Utilisez vos identifiants pour vous connecter
   - Vous arrivez sur le tableau de bord

3. **Commencer à utiliser l'application**
   - Ajoutez vos premiers patients
   - Créez des rendez-vous
   - Faites passer des questionnaires
   - Générez des documents PDF

## Configuration des intégrations (optionnel)

### Google Calendar

Pour synchroniser automatiquement vos rendez-vous avec Google Agenda :

1. Suivez le guide détaillé dans [INTEGRATIONS.md](INTEGRATIONS.md#-google-calendar---synchronisation-automatique)
2. Créez un projet Google Cloud et activez Google Calendar API
3. Téléchargez le fichier `google_credentials.json`
4. Placez-le à la racine du projet
5. Dans Google Agenda, partagez votre agenda avec l'email du compte de service (`client_email` du fichier JSON), droit « Apporter des modifications aux événements »
6. Renseignez l'agenda dans `.env` : `GOOGLE_CALENDAR_ID=votre_adresse@gmail.com` (sinon les rendez-vous partent dans l'agenda invisible du compte de service), puis relancez `python3 app.py`

✅ **Une fois configuré** : Tous les rendez-vous sont automatiquement synchronisés !

### SMS & WhatsApp (Twilio)

Pour envoyer des rappels automatiques par SMS ou WhatsApp :

1. Créez un compte sur [Twilio.com](https://www.twilio.com/try-twilio) (crédit gratuit offert)
2. Obtenez vos credentials (Account SID et Auth Token)
3. Ajoutez-les dans le fichier `.env` :

```bash
TWILIO_ACCOUNT_SID=votre_account_sid
TWILIO_AUTH_TOKEN=votre_auth_token
TWILIO_PHONE_NUMBER=+33123456789
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

ENABLE_REMINDERS=True
REMINDER_HOURS_BEFORE=24
REMINDER_METHOD=both  # ou 'sms' ou 'whatsapp'
```

4. Consultez le guide complet : [INTEGRATIONS.md](INTEGRATIONS.md#-notifications-sms--whatsapp)

✅ **Une fois configuré** : Les rappels partent automatiquement : vérification toutes les heures de 8h à 20h, un rappel unique par RDV environ 24h avant !

**Note** : Ces intégrations sont optionnelles. L'application fonctionne parfaitement sans elles.

## Utilisation

### Gestion des patients

**Créer un nouveau patient :**
1. Menu "Patients" > "Nouveau patient"
2. Remplir les informations personnelles
3. Ajouter les antécédents médicaux
4. Sélectionner le type de thérapie
5. Enregistrer

**Consulter un dossier patient :**
- Cliquer sur le nom du patient
- Voir l'historique des rendez-vous
- Accéder aux questionnaires passés
- Consulter les notes de séances

### Gestion des rendez-vous

**Créer un rendez-vous :**
1. Bouton "Nouveau rendez-vous" ou menu "Calendrier"
2. Sélectionner le patient
3. Choisir la date et l'heure
4. Définir le type de séance (TCC, ACT, Sophrologie, Hypnose, etc.)
5. Ajouter des notes si besoin
6. Enregistrer

L'application vérifie automatiquement la disponibilité du créneau.

### Questionnaires

**Faire passer un questionnaire :**
1. Aller dans le dossier du patient
2. Ou menu "Questionnaires" > Choisir un questionnaire
3. Sélectionner le patient
4. Le patient ou vous-même remplissez les réponses
5. Le score est calculé automatiquement
6. Ajouter des notes d'interprétation si besoin

**Questionnaires disponibles :**
- **HAD** : Anxiété et dépression (14 items)
- **BDI-II** : Intensité de la dépression
- **AAQ-II** : Flexibilité psychologique (ACT)
- **MAAS** : Pleine conscience
- **Suivi** : Évaluation rapide entre les séances

### Génération de documents PDF

**Générer un document :**
1. Depuis le dossier patient ou la séance
2. Cliquer sur "Générer PDF"
3. Le document est créé au format A4
4. Il est automatiquement téléchargé et archivé

**Types de documents disponibles :**
- Compte-rendu de séance
- Résultats de questionnaires
- Dossier patient complet

### Intégration Google (optionnel)

**Configuration Google API :**

1. Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activer les APIs :
   - Google Docs API
   - Google Sheets API
   - Google Drive API

3. Créer un compte de service
4. Télécharger le fichier JSON des credentials
5. Renommer en `google_credentials.json`
6. Placer à la racine du projet

**Utilisation :**
- Export de séances vers Google Docs
- Création de feuilles de suivi dans Google Sheets
- Partage de documents avec d'autres professionnels

## Structure du projet

```
cedricIA/
├── app.py                      # Application Flask principale
├── config.py                   # Configuration
├── extensions.py               # Extensions Flask (DB, Login)
├── models.py                   # Modèles de données
├── init_db.py                  # Script d'initialisation
├── requirements.txt            # Dépendances Python
├── .env                        # Configuration (à créer)
├── routes/                     # Routes Flask (blueprints)
│   ├── auth.py                 # Authentification
│   ├── patients.py             # Gestion patients
│   ├── appointments.py         # Rendez-vous
│   ├── questionnaires.py       # Questionnaires
│   └── documents.py            # Génération PDF
├── templates/                  # Templates HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── auth/
│   ├── patients/
│   ├── appointments/
│   └── questionnaires/
├── static/                     # Fichiers statiques
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── utils/                      # Utilitaires
    ├── pdf_generator.py        # Génération PDF
    ├── google_integration.py   # Intégration Google
    └── predefined_questionnaires.py  # Questionnaires prédéfinis
```

## Technologies utilisées

- **Backend** : Python 3.8+, Flask 3.0
- **Base de données** : SQLite (peut être changé pour PostgreSQL)
- **Frontend** : HTML5, CSS3, JavaScript
- **Génération PDF** : ReportLab
- **Intégration** : Google API Client

## Sécurité et confidentialité

⚠️ **Important** : Cette application contient des données médicales sensibles.

**Bonnes pratiques :**
1. Changez la `SECRET_KEY` dans le fichier `.env`
2. Utilisez HTTPS en production
3. Sauvegardez régulièrement la base de données
4. Respectez le RGPD et les obligations légales
5. Ne partagez pas vos credentials Google

**Sauvegardes :**
```bash
# Copier la base de données
cp cabinet.db cabinet_backup_$(date +%Y%m%d).db

# Sauvegarder les PDFs générés
tar -czf pdfs_backup_$(date +%Y%m%d).tar.gz generated_pdfs/
```

## Déploiement en production

Pour un déploiement professionnel, il est recommandé de :

1. **Utiliser un serveur web robuste**
   - Gunicorn ou uWSGI
   - Nginx comme reverse proxy

2. **Base de données production**
   - PostgreSQL recommandé
   - Modifier `DATABASE_URL` dans `.env`

3. **HTTPS obligatoire**
   - Let's Encrypt pour certificat gratuit
   - Protection des données médicales

4. **Variables d'environnement**
   - Désactiver le mode DEBUG
   - Utiliser des secrets robustes

## Support et personnalisation

### Personnaliser les questionnaires

Modifier le fichier `utils/predefined_questionnaires.py` pour :
- Ajouter de nouveaux questionnaires
- Modifier les questions existantes
- Adapter les méthodes de cotation

### Ajouter des types de thérapie

Dans le fichier `templates/patients/new.html`, section "Type de thérapie" :
```html
<option value="Votre_Type">Votre nouveau type</option>
```

### Modifier les horaires d'ouverture

Dans `routes/appointments.py`, fonction `available_slots` :
```python
opening_time = time(9, 0)   # Heure d'ouverture
closing_time = time(18, 0)  # Heure de fermeture
slot_duration = 60          # Durée des créneaux en minutes
```

## Licence

MIT License - Voir le fichier LICENSE

## Contribution

Les contributions sont les bienvenues !

Pour contribuer :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Contact et assistance

Pour toute question ou suggestion :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les logs en cas d'erreur

## Remerciements

Développé pour simplifier la gestion des cabinets de psychothérapie et améliorer le suivi des patients.

---

**Note** : Cette application est un outil d'aide à la gestion. Elle ne remplace pas le jugement clinique professionnel et doit être utilisée en conformité avec les réglementations locales sur les données de santé.
