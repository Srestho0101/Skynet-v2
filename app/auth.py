from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User, Anime, Character
from app.forms import RegistrationForm, LoginForm, CharacterSelectionForm
from app.utils import claim_character

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created! Now select your anime character.', 'success')
            return redirect(url_for('auth.select_anime', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
    return render_template('register.html', form=form)

@auth_bp.route('/select_anime/<int:user_id>', methods=['GET'])
def select_anime(user_id):
    user = User.query.get(user_id)
    if not user or user.character:
        flash('Invalid request or character already selected', 'error')
        return redirect(url_for('auth.login'))
    anime_list = Anime.query.all()
    return render_template('select_anime.html', anime_list=anime_list, user_id=user_id)

@auth_bp.route('/select_character/<int:user_id>/<int:anime_id>', methods=['GET'])
def select_character(user_id, anime_id):
    user = User.query.get(user_id)
    if not user or user.character:
        flash('Invalid request or character already selected', 'error')
        return redirect(url_for('auth.login'))
    anime = Anime.query.get(anime_id)
    if not anime:
        flash('Anime not found', 'error')
        return redirect(url_for('auth.select_anime', user_id=user_id))
    characters = Character.query.filter_by(anime_id=anime_id, taken=False).all()
    form = CharacterSelectionForm()
    return render_template('select_character.html', user_id=user_id, anime=anime, characters=characters, form=form)

@auth_bp.route('/claim_character', methods=['POST'])
def claim_character_route():
    user_id = request.form.get('user_id', type=int)
    character_id = request.form.get('character_id', type=int)
    if not user_id or not character_id:
        flash('Invalid request', 'error')
        return redirect(url_for('auth.login'))
    success, message = claim_character(user_id, character_id)
    if success:
        flash(message, 'success')
        user = User.query.get(user_id)
        login_user(user)
        return redirect(url_for('main.feed'))
    else:
        flash(message, 'error')
        character = Character.query.get(character_id)
        if character:
            return redirect(url_for('auth.select_character', user_id=user_id, anime_id=character.anime_id))
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.feed'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
