from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from .config import Config

# ORM global
db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    # 1) Base de données
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

    # 2) Auth0 / OAuth
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
    app.oauth = oauth

    # 3) Chargement des modules CLI
    from .modules import load_modules
    load_modules()

    # 4) Flask-Login + Blueprints
    from .routes import login_manager, bp as routes_bp
    from .cve_ai  import bp_cve

    login_manager.login_view = "routes.login"
    login_manager.init_app(app)
    app.login_manager = login_manager

    # Enregistrement des blueprints
    app.register_blueprint(routes_bp)
    app.register_blueprint(bp_cve)

    return app

