from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required
from models import Document, Patient, TherapySession, QuestionnaireResponse
from extensions import db
from utils.pdf_generator import PDFGenerator
from utils.google_integration import GoogleDocsIntegration
import os

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/generate-session-report/<int:session_id>')
@login_required
def generate_session_report(session_id):
    """Générer un compte-rendu de séance en PDF"""
    session = TherapySession.query.get_or_404(session_id)

    pdf_gen = PDFGenerator()
    filename = f"compte_rendu_seance_{session.id}_{session.session_date.strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(current_app.config['PDF_FOLDER'], filename)

    pdf_gen.generate_session_report(session, filepath)

    # Enregistrer le document
    document = Document(
        patient_id=session.patient_id,
        document_type='Compte-rendu de séance',
        title=f"Séance du {session.session_date.strftime('%d/%m/%Y')}",
        file_path=filepath
    )
    db.session.add(document)
    db.session.commit()

    flash('Document généré avec succès !', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@bp.route('/generate-questionnaire-report/<int:response_id>')
@login_required
def generate_questionnaire_report(response_id):
    """Générer un rapport de questionnaire en PDF"""
    response = QuestionnaireResponse.query.get_or_404(response_id)

    pdf_gen = PDFGenerator()
    filename = f"questionnaire_{response.questionnaire.short_name}_{response.patient_id}_{response.completed_at.strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(current_app.config['PDF_FOLDER'], filename)

    pdf_gen.generate_questionnaire_report(response, filepath)

    # Enregistrer le document
    document = Document(
        patient_id=response.patient_id,
        document_type='Questionnaire',
        title=f"{response.questionnaire.name} - {response.completed_at.strftime('%d/%m/%Y')}",
        file_path=filepath
    )
    db.session.add(document)
    db.session.commit()

    flash('Document généré avec succès !', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@bp.route('/generate-patient-file/<int:patient_id>')
@login_required
def generate_patient_file(patient_id):
    """Générer le dossier patient complet en PDF"""
    patient = Patient.query.get_or_404(patient_id)

    pdf_gen = PDFGenerator()
    filename = f"dossier_patient_{patient.id}_{patient.last_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(current_app.config['PDF_FOLDER'], filename)

    pdf_gen.generate_patient_file(patient, filepath)

    # Enregistrer le document
    document = Document(
        patient_id=patient_id,
        document_type='Dossier patient',
        title=f"Dossier complet - {patient.first_name} {patient.last_name}",
        file_path=filepath
    )
    db.session.add(document)
    db.session.commit()

    flash('Dossier patient généré avec succès !', 'success')
    return send_file(filepath, as_attachment=True, download_name=filename)

@bp.route('/export-to-gdocs/<int:session_id>')
@login_required
def export_to_gdocs(session_id):
    """Exporter une séance vers Google Docs"""
    session = TherapySession.query.get_or_404(session_id)

    google_integration = GoogleDocsIntegration()

    try:
        doc_id = google_integration.create_session_document(session)

        # Enregistrer le document
        document = Document(
            patient_id=session.patient_id,
            document_type='Compte-rendu de séance (Google Docs)',
            title=f"Séance du {session.session_date.strftime('%d/%m/%Y')}",
            google_doc_id=doc_id
        )
        db.session.add(document)
        db.session.commit()

        flash(f'Document exporté vers Google Docs ! ID: {doc_id}', 'success')
        return redirect(url_for('patients.view_patient', patient_id=session.patient_id))

    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'error')
        return redirect(url_for('patients.view_patient', patient_id=session.patient_id))

@bp.route('/patient/<int:patient_id>')
@login_required
def patient_documents(patient_id):
    """Liste des documents d'un patient"""
    patient = Patient.query.get_or_404(patient_id)
    documents = Document.query.filter_by(patient_id=patient_id).order_by(db.desc(Document.created_at)).all()

    return render_template('documents/list.html', patient=patient, documents=documents)
