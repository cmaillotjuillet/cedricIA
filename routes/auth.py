from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import User
from extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Identifiants incorrects', 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription (première utilisation)"""
    # Vérifier s'il y a déjà un utilisateur
    if User.query.first():
        flash('Un compte existe déjà.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        specialties = request.form.get('specialties')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            specialties=specialties
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')
