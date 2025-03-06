from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_overrides=None):
    app = Flask(__name__)

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_overrides:
        app.config.update(config_overrides)

    # Load models
    from todo.models import db
    from todo.models.todo import Todo
    db.init_app(app)

    # Create database tables if not exists
    with app.app_context():
        db.create_all()

    # Register blueprints (make sure this is correct)
    from todo.views.routes import api  # ✅ This must match your actual routes file
    app.register_blueprint(api, url_prefix="/api/v1")  # ✅ Ensure prefix matches tests

    return app
