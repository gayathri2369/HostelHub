import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ENABLE CORS
    CORS(app)

    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'dev-secret-change-me'
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///hostelhub.db'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['UPLOAD_FOLDER'] = os.path.join(
        app.root_path,
        'uploads'
    )

    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth_routes import auth_bp
    from .main_routes import main_bp
    from .api_routes import api_bp

    app.register_blueprint(auth_bp)

    app.register_blueprint(main_bp)

    app.register_blueprint(api_bp, url_prefix='/api')

    @app.cli.command('init-db')
    def init_db_command():
        from .seed import seed_data

        db.drop_all()
        db.create_all()

        seed_data()

        print('Database initialized with sample data.')

    with app.app_context():
        db.create_all()

    return app