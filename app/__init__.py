from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes import main_bp
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        seed_database()

    return app

def seed_database():
    from app.models import Anime, Character
    if Anime.query.first():
        return

    anime_data = [
        {
            'name': 'Neon Genesis Evangelion',
            'characters': [
                {'name': 'Shinji Ikari', 'avatar': '🧑‍🚀'},
                {'name': 'Rei Ayanami', 'avatar': '👩‍🦰'},
                {'name': 'Asuka Langley', 'avatar': '👩‍🦱'},
            ]
        },
        {
            'name': 'Attack on Titan',
            'characters': [
                {'name': 'Eren Yeager', 'avatar': '😤'},
                {'name': 'Mikasa Ackerman', 'avatar': '⚔️'},
                {'name': 'Arwin Arlet', 'avatar': '🤓'},
                {'name': 'Levi Ackerman', 'avatar': '🧛'},
            ]
        }
    ]

    try:
        for anime_info in anime_data:
            anime = Anime(name=anime_info['name'])
            db.session.add(anime)
            db.session.flush()
            for char_info in anime_info['characters']:
                character = Character(
                    name=char_info['name'],
                    anime_id=anime.id,
                    avatar=char_info['avatar'],
                    taken=False
                )
                db.session.add(character)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")
