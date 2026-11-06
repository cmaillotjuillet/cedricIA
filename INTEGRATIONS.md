# Guide d'intégration - Google Calendar & Notifications SMS/WhatsApp

Ce guide explique comment configurer les intégrations avec Google Calendar et Twilio pour les rappels SMS/WhatsApp.

## 📅 Google Calendar - Synchronisation automatique

### Configuration

#### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez-en un
3. Notez le nom du projet

#### 2. Activer les APIs nécessaires

Dans Google Cloud Console :
1. Menu "APIs et services" > "Bibliothèque"
2. Recherchez et activez ces APIs :
   - **Google Calendar API**
   - **Google Docs API**
   - **Google Sheets API**
   - **Google Drive API**

#### 3. Créer un compte de service

1. Menu "APIs et services" > "Identifiants"
2. Cliquez sur "Créer des identifiants" > "Compte de service"
3. Donnez un nom : `cedric-ia-service`
4. Cliquez sur "Créer et continuer"
5. Rôle : "Éditeur" (ou "Propriétaire" pour tous les droits)
6. Cliquez sur "Continuer" puis "OK"

#### 4. Générer la clé JSON

1. Cliquez sur le compte de service créé
2. Onglet "Clés"
3. "Ajouter une clé" > "Créer une clé"
4. Format : JSON
5. Le fichier `cedric-ia-service-xxxxx.json` est téléchargé

#### 5. Installer le fichier de credentials

1. Renommez le fichier téléchargé en `google_credentials.json`
2. Placez-le à la racine du projet CedricIA :
```
cedricIA/
├── google_credentials.json  ← ICI
├── app.py
├── requirements.txt
└── ...
```

3. **Important** : Ce fichier ne doit JAMAIS être committé dans Git (déjà dans .gitignore)

#### 6. Partager votre calendrier avec le compte de service

1. Ouvrez [Google Calendar](https://calendar.google.com)
2. Paramètres > Vos calendriers > Sélectionnez votre calendrier
3. "Partager avec des personnes spécifiques"
4. Ajoutez l'email du compte de service (dans le fichier JSON : `client_email`)
5. Permissions : "Apporter des modifications aux événements"
6. Enregistrez

#### 7. Indiquer votre agenda dans `.env`

Ajoutez dans le fichier `.env` l'identifiant de l'agenda partagé (pour un agenda Gmail principal, c'est votre adresse Gmail ; sinon : Paramètres de l'agenda > « Intégrer l'agenda » > « ID de l'agenda ») :

```
GOOGLE_CALENDAR_ID=votre_adresse@gmail.com
```

⚠️ Sans cette ligne, les rendez-vous sont créés dans l'agenda propre au compte de service, que vous ne voyez pas.

Redémarrez ensuite l'application (`python3 app.py`).

### Utilisation

Une fois configuré, **chaque nouveau rendez-vous sera automatiquement** :
- ✅ Ajouté à votre Google Calendar
- ✅ Synchronisé en temps réel
- ✅ Modifiable depuis l'app ou Google Calendar
- ✅ Supprimé si annulé

**Fonctionnalités disponibles :**
- Création automatique d'événements
- Mise à jour des rendez-vous modifiés
- Suppression des rendez-vous annulés
- Rappels Google Calendar (24h et 1h avant)

---

## 📱 Notifications SMS & WhatsApp

### Configuration Twilio

#### 1. Créer un compte Twilio

1. Allez sur [Twilio.com](https://www.twilio.com/try-twilio)
2. Créez un compte gratuit (crédit offert pour tester)
3. Vérifiez votre email et numéro de téléphone

#### 2. Obtenir vos credentials

Dans le [Twilio Console](https://console.twilio.com/) :
1. Notez votre **Account SID**
2. Notez votre **Auth Token** (cliquez sur l'œil pour révéler)

#### 3. Acheter un numéro de téléphone

**Pour les SMS :**
1. Dans Twilio Console : "Phone Numbers" > "Buy a number"
2. Sélectionnez "France" (+33)
3. Cochez "SMS" dans les capacités
4. Choisissez un numéro et achetez-le (~1€/mois)
5. Notez le numéro au format international : `+33XXXXXXXXX`

**Pour WhatsApp (mode test) :**
1. Dans Twilio Console : "Messaging" > "Try it out" > "Send a WhatsApp message"
2. Notez le numéro WhatsApp sandbox : `whatsapp:+14155238886` (ou autre selon votre région)
3. Suivez les instructions pour rejoindre le sandbox

#### 4. Rejoindre le WhatsApp Sandbox

**Important pour tester WhatsApp :**
1. Depuis votre WhatsApp, ajoutez le numéro Twilio
2. Envoyez le code de connexion (ex: `join abc-def`)
3. Vous recevez une confirmation
4. Vous pouvez maintenant recevoir des messages du sandbox

**Pour la production WhatsApp :**
- Demandez l'approbation de votre compte WhatsApp Business
- Processus plus long mais permet l'envoi sans restriction

#### 5. Configuration dans CedricIA

Éditez le fichier `.env` (créez-le depuis `.env.example` si nécessaire) :

```bash
# Configuration Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=votre_auth_token_secret
TWILIO_PHONE_NUMBER=+33123456789
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Configuration des rappels
ENABLE_REMINDERS=True
REMINDER_HOURS_BEFORE=24
REMINDER_METHOD=both  # ou 'sms' ou 'whatsapp'
```

### Utilisation

#### Rappels automatiques

Les rappels sont envoyés **automatiquement** (vérification toutes les heures de 8h à 20h, un rappel unique par RDV environ 24h avant) pour :
- Les rendez-vous du lendemain (24h avant)
- Format professionnel avec date, heure, type de séance
- Message personnalisé avec le prénom du patient

**Exemple de message envoyé :**
```
Bonjour Marie,

Rappel de votre rendez-vous :
📅 Date : 15/01/2026
⏰ Heure : 14:30
⏱ Durée : 60 minutes
💼 Type : TCC

En cas d'empêchement, merci de prévenir le plus tôt possible.

À bientôt !
```

#### Rappels manuels

Depuis la fiche d'un rendez-vous :
1. Cliquez sur "Envoyer un rappel"
2. Choisissez SMS, WhatsApp ou les deux
3. Le patient reçoit immédiatement le message

#### Test des notifications

1. Menu "Notifications" > "Tester les notifications"
2. Entrez votre numéro (pour tester)
3. Choisissez SMS ou WhatsApp
4. Envoyez le test

**Si ça fonctionne** : ✅ Configuration OK !
**Si ça ne fonctionne pas** : Vérifiez vos credentials dans `.env`

### Tarification Twilio

**Mode test (crédit gratuit) :**
- Crédit initial : ~15-20€
- Utilisable pour tous les tests

**Mode production :**
- SMS France : ~0.08€ par SMS
- WhatsApp : ~0.005€ par message (bien moins cher !)
- Numéro de téléphone : ~1€/mois

💡 **Astuce** : WhatsApp est 16 fois moins cher que les SMS !

---

## 🔧 Configuration avancée

### Modifier l'heure d'envoi des rappels

Dans `utils/scheduler.py`, ligne ~50 :
```python
# Rappels : vérification toutes les heures de 8h à 20h
self.scheduler.add_job(
    func=lambda: send_automatic_reminders(self.app),
    trigger=CronTrigger(hour='8-20', minute=0),  # Modifier la plage ici
    ...
)
```

Exemples :
- `hour='9-19', minute=0` : vérification toutes les heures de 9h à 19h
- `hour='8-20', minute=30` : vérification à la demie, de 8h30 à 20h30

Chaque RDV ne reçoit qu'un seul rappel : dès qu'il entre dans la fenêtre de `REMINDER_HOURS_BEFORE` heures, le rappel part à la vérification suivante.

### Modifier le délai de rappel

Dans `.env` :
```bash
REMINDER_HOURS_BEFORE=48  # Rappels 48h avant
REMINDER_HOURS_BEFORE=12  # Rappels 12h avant
```

### Personnaliser les messages

Dans `utils/notifications.py`, méthode `_format_appointment_message()`, ligne ~120 :
```python
def _format_appointment_message(self, appointment):
    # Personnalisez le message ici
    message = f"""Bonjour {patient.first_name},

Rappel de votre rendez-vous :
...
```

---

## 🚨 Dépannage

### Google Calendar ne fonctionne pas

**Problème** : "Google Calendar API non configurée"
- ✅ Vérifiez que `google_credentials.json` existe
- ✅ Vérifiez que les APIs sont activées
- ✅ Vérifiez que le calendrier est partagé avec le compte de service

**Problème** : "Permission denied"
- ✅ Partagez le calendrier avec l'email du compte de service
- ✅ Donnez les droits "Apporter des modifications"

### SMS/WhatsApp ne fonctionnent pas

**Problème** : "Twilio n'est pas configuré"
- ✅ Vérifiez les variables dans `.env`
- ✅ Redémarrez l'application après modification

**Problème** : "Numéro non vérifié" (mode test)
- ✅ Dans Twilio Console, vérifiez le numéro de destination
- ✅ Menu "Phone Numbers" > "Verified Caller IDs"

**Problème** : WhatsApp "Not a valid WhatsApp recipient"
- ✅ Rejoignez d'abord le sandbox WhatsApp
- ✅ Envoyez le code de connexion depuis WhatsApp
- ✅ Attendez la confirmation

**Problème** : "Insufficient funds"
- ✅ Rechargez votre compte Twilio
- ✅ Minimum 5€ recommandé

### Les rappels automatiques ne partent pas

**Vérifications :**
1. L'application doit tourner en continu (pas juste pour les consultations)
2. Variable `ENABLE_REMINDERS=True` dans `.env`
3. Vérifier les logs au démarrage : "Scheduler démarré"
4. Tester manuellement : Menu Notifications > Envoyer tous les rappels

---

## 📊 Monitoring

### Vérifier les rappels en attente

Menu "Notifications" > "Rappels en attente"
- Liste des rendez-vous qui recevront un rappel
- Vérifier les numéros de téléphone

### Historique des rappels

Menu "Notifications" > "Historique"
- Liste des rappels déjà envoyés
- Statut de chaque envoi

### Logs

Les logs du scheduler s'affichent dans la console :
```
INFO:__main__:Scheduler démarré
INFO:utils.scheduler:Tâche planifiée : vérification des rappels toutes les heures de 8h à 20h
INFO:__main__:Rappels envoyés : 5/5
```

---

## 🎯 Meilleures pratiques

### Sécurité

1. ✅ **Ne commitez JAMAIS** `google_credentials.json` dans Git
2. ✅ **Ne partagez JAMAIS** vos credentials Twilio
3. ✅ Utilisez `.env` pour toutes les config sensibles
4. ✅ Changez les tokens si compromis

### Données patients

1. ✅ Vérifiez le consentement patient pour SMS/WhatsApp
2. ✅ Respectez le RGPD (données médicales)
3. ✅ Proposez opt-out des rappels si demandé

### Production

1. ✅ Utilisez un vrai compte WhatsApp Business (pas sandbox)
2. ✅ Configurez un domaine vérifié pour WhatsApp
3. ✅ Mettez en place des alertes sur les échecs d'envoi
4. ✅ Surveillez votre crédit Twilio

---

## 💡 Astuces

### Réduire les coûts

- Utilisez **WhatsApp** plutôt que SMS (16x moins cher)
- Configurez `REMINDER_METHOD=whatsapp`
- SMS uniquement en backup si WhatsApp échoue

### Améliorer le taux de lecture

- Envoyez les rappels le soir (18h-20h) pour le lendemain
- Personnalisez les messages avec le prénom
- Testez différents formats de message

### Automatisation complète

Avec cette configuration, **zéro action manuelle** :
1. ✅ Créez un RDV dans l'app → Ajouté dans Google Agenda
2. ✅ 24h avant → Rappel automatique SMS/WhatsApp
3. ✅ Patient prévenu → Moins de no-show
4. ✅ Vous gérez tout depuis l'app ou Google Calendar

---

## 📞 Support

**Documentation officielle :**
- [Twilio SMS](https://www.twilio.com/docs/sms)
- [Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)
- [Google Calendar API](https://developers.google.com/calendar/api/guides/overview)

**Problèmes connus :**
Consultez le README.md ou ouvrez une issue sur GitHub.

**Besoin d'aide ?**
Vérifiez d'abord ce guide, puis les logs de l'application.

## 📱 Accès depuis le téléphone (Tailscale)

L'application reste sur le Mac : Tailscale crée un tunnel privé et chiffré
entre vos appareils. Rien n'est publié sur internet.

1. Installez Tailscale sur le Mac (App Store ou tailscale.com/download) et sur
   le téléphone, connectés au même compte.
2. Sur le Mac, avec CedricIA lancé, dans Terminal :
   `tailscale serve --bg 5050`
   (si « command not found » :
   `/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --bg 5050`).
   Acceptez l'activation des certificats HTTPS si elle est proposée.
3. La commande affiche une adresse `https://….ts.net` : ouvrez-la sur le
   téléphone et ajoutez-la à l'écran d'accueil.

Le Mac doit rester allumé (Réglages système > Énergie : empêcher la suspension
automatique) et CedricIA lancé.
