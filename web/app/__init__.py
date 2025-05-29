# web/app/__init__.py

"""
Initialisation de l’application Flask TSAR :
  • config (classe Config)
  • base de données (SQLAlchemy)
  • Auth0 (OAuth)
  • chargement des modules CLI
  • configuration de Flask-Login
  • enregistrement du blueprint principal
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from .config import Config

# ─── ORM global ─────────────────────────────────────────────────────────────
db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    # ─── 1) Base de données ─────────────────────────────────────────────────
    db.init_app(app)
    with app.app_context():
        from . import models      # must come before create_all()
        db.create_all()

    # ─── 2) Auth0 / OAuth ────────────────────────────────────────────────────
    oauth = OAuth(app)
    oauth.register(
        name="auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=(
            f'https://{app.config["AUTH0_DOMAIN"]}'
            '/.well-known/openid-configuration'
        ),
    )
    app.oauth = oauth  # accessible via current_app.oauth

    # ─── 3) Chargement des modules CLI ────────────────────────────────────────
    from .modules import load_modules
    load_modules()

    # ─── 4) Flask-Login ───────────────────────────────────────────────────────
    # Importez ici votre login_manager et votre blueprint (bp) de routes.py
    from .routes import login_manager, bp as routes_bp

    # Définissez la vue de login par défaut
    login_manager.login_view = "routes.login"
    # Attachez-le à l’app
    login_manager.init_app(app)
    # exposez-le explicitement pour que current_app.login_manager existe
    app.login_manager = login_manager

    # ─── 5) Enregistrement du blueprint ──────────────────────────────────────
    app.register_blueprint(routes_bp)

    return app

