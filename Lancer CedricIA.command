#!/bin/bash
# Double-cliquez sur ce fichier pour ouvrir CedricIA.
# Laissez la fenêtre Terminal ouverte pendant l'utilisation ; fermez-la pour arrêter.

cd "$(dirname "$0")" || exit 1
PORT=5050

echo "Démarrage de CedricIA..."

# Installer les composants nécessaires la première fois seulement
if ! python3 -c "import flask, flask_sqlalchemy, flask_login, reportlab, googleapiclient, twilio, apscheduler, dotenv" 2>/dev/null; then
    echo "Première utilisation : installation des composants (quelques minutes)..."
    python3 -m pip install --user -r requirements.txt || { echo "Échec de l'installation."; read -r -p "Appuyez sur Entrée pour fermer."; exit 1; }
fi

# Créer ou compléter la base de données (sans rien effacer)
python3 init_db.py > /dev/null

# Ouvrir le navigateur dès que l'application répond
(
    for _ in $(seq 1 30); do
        sleep 1
        if curl -s -o /dev/null "http://127.0.0.1:$PORT/"; then
            open "http://127.0.0.1:$PORT/"
            break
        fi
    done
) &

PORT=$PORT python3 app.py
