import os
import secrets
from werkzeug.utils import secure_filename
from app import db
from app.models import Character, User

def allowed_file(filename, config):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']

def save_upload_file(file, config):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename, config):
        return None
    filename = secure_filename(file.filename)
    filename = f"{secrets.token_hex(8)}__{filename}"
    filepath = os.path.join(config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return os.path.join('uploads', filename)

def claim_character(user_id, character_id):
    character = Character.query.get(character_id)
    if not character:
        return False, "Character not found"
    if character.taken:
        return False, "This character has already been claimed"
    user = User.query.get(user_id)
    if user and user.character:
        return False, "You already have a character"
    character.taken = True
    character.user_id = user_id
    db.session.commit()
    return True, f"You are now {character.name}!"

def get_available_characters_by_anime(anime_id):
    return Character.query.filter_by(anime_id=anime_id, taken=False).all()

def delete_post_file(image_path, config):
    if image_path:
        full_path = os.path.join(config['UPLOAD_FOLDER'], image_path.replace('uploads/', ''))
        if os.path.exists(full_path):
            os.remove(full_path)
