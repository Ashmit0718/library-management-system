import os
from flask import Flask
from app.config import config_map
from app.extensions import db, migrate, bcrypt, cors
import app.models  # noqa: ensure models are registered with SQLAlchemy


def create_app(env=None):
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map[env])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

    # Blueprints
    from app.routes.auth      import auth_bp
    from app.routes.books     import books_bp
    from app.routes.borrows   import borrows_bp
    from app.routes.users     import users_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(analytics_bp)

    @app.route("/api/health")
    def health():
        return {"status": "ok", "env": env}

    return app
