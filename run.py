from dotenv import load_dotenv
import os
from app import create_app, db

load_dotenv()
app = create_app(os.getenv('FLASK_ENV', 'production'))

@app.shell_context_processor
def make_shell_context():
    from app import models
    return {
        'db': db,
        'User': models.User,
        'Character': models.Character,
        'Anime': models.Anime,
        'Post': models.Post,
        'Like': models.Like
    }

if __name__ == '__main__':
    app.run()