from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

class PDFGenerator:
    """Générateur de documents PDF au format A4"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Configurer les styles personnalisés"""
        # Style pour le titre
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8
        ))

    def generate_session_report(self, session, filepath):
        """Générer un compte-rendu de séance"""
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)

        story = []

        # En-tête
        story.append(Paragraph("COMPTE-RENDU DE SÉANCE", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Informations patient
        patient = session.patient
        info_data = [
            ['Patient:', f"{patient.first_name} {patient.last_name}"],
            ['Date de la séance:', session.session_date.strftime('%d/%m/%Y')],
            ['Type de thérapie:', session.therapy_type or 'Non spécifié'],
            ['Numéro de séance:', str(session.session_number) if session.session_number else 'N/A']
        ]

        info_table = Table(info_data, colWidths=[5*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.7*cm))

        # Objectifs
        if session.objectives:
            story.append(Paragraph("Objectifs de la séance", self.styles['CustomHeading']))
            story.append(Paragraph(session.objectives, self.styles['CustomBody']))
            story.append(Spacer(1, 0.5*cm))

        # Interventions
        if session.interventions:
            story.append(Paragraph("Interventions thérapeutiques", self.styles['CustomHeading']))
            story.append(Paragraph(session.interventions, self.styles['CustomBody']))
            story.append(Spacer(1, 0.5*cm))

        # Progrès du patient
        if session.patient_progress:
            story.append(Paragraph("Progrès observés", self.styles['CustomHeading']))
            story.append(Paragraph(session.patient_progress, self.styles['CustomBody']))
            story.append(Spacer(1, 0.5*cm))

        # Évaluations
        if session.mood_score or session.anxiety_score:
            story.append(Paragraph("Évaluations", self.styles['CustomHeading']))
            eval_data = []
            if session.mood_score:
                eval_data.append(['Humeur:', f"{session.mood_score}/10"])
            if session.anxiety_score:
                eval_data.append(['Anxiété:', f"{session.anxiety_score}/10"])

            eval_table = Table(eval_data, colWidths=[5*cm, 12*cm])
            eval_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
            ]))
            story.append(eval_table)
            story.append(Spacer(1, 0.5*cm))

        # Exercices à faire
        if session.homework:
            story.append(Paragraph("Exercices à faire", self.styles['CustomHeading']))
            story.append(Paragraph(session.homework, self.styles['CustomBody']))
            story.append(Spacer(1, 0.5*cm))

        # Prochaine séance
        if session.next_session_plan:
            story.append(Paragraph("Plan pour la prochaine séance", self.styles['CustomHeading']))
            story.append(Paragraph(session.next_session_plan, self.styles['CustomBody']))

        # Pied de page
        story.append(Spacer(1, 1*cm))
        footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Générer le PDF
        doc.build(story)

    def generate_questionnaire_report(self, response, filepath):
        """Générer un rapport de questionnaire"""
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)

        story = []

        # En-tête
        story.append(Paragraph(f"QUESTIONNAIRE: {response.questionnaire.name.upper()}", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Informations
        patient = response.patient
        info_data = [
            ['Patient:', f"{patient.first_name} {patient.last_name}"],
            ['Date de passation:', response.completed_at.strftime('%d/%m/%Y')],
            ['Questionnaire:', response.questionnaire.name],
            ['Score total:', f"{response.total_score:.1f}" if response.total_score else 'N/A']
        ]

        info_table = Table(info_data, colWidths=[5*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.7*cm))

        # Réponses
        if response.responses:
            story.append(Paragraph("Réponses détaillées", self.styles['CustomHeading']))

            questions = response.questionnaire.questions or []
            for idx, question in enumerate(questions, 1):
                question_id = str(question.get('id', idx))
                question_text = question.get('text', f'Question {idx}')
                answer = response.responses.get(question_id, 'Non répondu')

                story.append(Paragraph(f"<b>{idx}. {question_text}</b>", self.styles['CustomBody']))
                story.append(Paragraph(f"Réponse: {answer}", self.styles['CustomBody']))
                story.append(Spacer(1, 0.3*cm))

        # Interprétation
        if response.interpretation:
            story.append(Paragraph("Interprétation", self.styles['CustomHeading']))
            story.append(Paragraph(response.interpretation, self.styles['CustomBody']))
            story.append(Spacer(1, 0.5*cm))

        # Notes
        if response.notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(response.notes, self.styles['CustomBody']))

        # Pied de page
        story.append(Spacer(1, 1*cm))
        footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Générer le PDF
        doc.build(story)

    def generate_patient_file(self, patient, filepath):
        """Générer le dossier patient complet"""
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)

        story = []

        # En-tête
        story.append(Paragraph("DOSSIER PATIENT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Informations personnelles
        story.append(Paragraph("Informations personnelles", self.styles['CustomHeading']))

        info_data = [
            ['Nom:', patient.last_name or ''],
            ['Prénom:', patient.first_name or ''],
            ['Date de naissance:', patient.date_of_birth.strftime('%d/%m/%Y') if patient.date_of_birth else 'Non renseignée'],
            ['Email:', patient.email or 'Non renseigné'],
            ['Téléphone:', patient.phone or 'Non renseigné'],
            ['Adresse:', patient.address or 'Non renseignée']
        ]

        info_table = Table(info_data, colWidths=[5*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.7*cm))

        # Informations médicales
        story.append(Paragraph("Informations médicales", self.styles['CustomHeading']))

        medical_data = [
            ['Antécédents médicaux:', patient.medical_history or 'Aucun'],
            ['Traitements en cours:', patient.current_treatments or 'Aucun'],
            ['Allergies:', patient.allergies or 'Aucune'],
            ['Contact d\'urgence:', patient.emergency_contact or 'Non renseigné']
        ]

        medical_table = Table(medical_data, colWidths=[5*cm, 12*cm])
        medical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        story.append(medical_table)
        story.append(Spacer(1, 0.7*cm))

        # Informations thérapeutiques
        story.append(Paragraph("Informations thérapeutiques", self.styles['CustomHeading']))

        therapy_data = [
            ['Type de thérapie:', patient.therapy_type or 'Non spécifié'],
            ['Première séance:', patient.first_session_date.strftime('%d/%m/%Y') if patient.first_session_date else 'Non renseignée']
        ]

        therapy_table = Table(therapy_data, colWidths=[5*cm, 12*cm])
        therapy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))

        story.append(therapy_table)
        story.append(Spacer(1, 0.5*cm))

        # Notes
        if patient.notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(patient.notes, self.styles['CustomBody']))

        # Pied de page
        story.append(Spacer(1, 1*cm))
        footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Générer le PDF
        doc.build(story)
