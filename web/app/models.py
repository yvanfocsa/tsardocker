# web/app/models.py

"""
Modèles SQLAlchemy pour TSAR :

* **Report** : PDF chiffré généré après l’exécution d’un module.
* **ScanLog** : trace légère de chaque exécution “live” (terminal),
  affichée dans le tableau « Historique » du dashboard.
"""

from datetime import datetime
from . import db


# ───────────────────────────── Report ──────────────────────────────
class Report(db.Model):
    __tablename__ = "reports"

    id         = db.Column(db.Integer, primary_key=True)
    user_sub   = db.Column(db.String(128), nullable=False)   # sub Auth0
    filename   = db.Column(db.Text,        nullable=False)   # nom du PDF
    pdf_data   = db.Column(db.LargeBinary, nullable=False)   # PDF chiffré
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Report #{self.id} {self.filename}>"


# ───────────────────────────── ScanLog ─────────────────────────────
class ScanLog(db.Model):
    __tablename__ = "scan_logs"

    id         = db.Column(db.Integer, primary_key=True)
    user_sub   = db.Column(db.String(128), nullable=False)   # sub Auth0
    module     = db.Column(db.String(64),  nullable=False)   # ex. "nmap"
    target     = db.Column(db.Text,        nullable=True)    # cible scannée
    mode       = db.Column(db.String(16),  nullable=False)   # quick / full / …
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self) -> str:
        return (f"<ScanLog #{self.id} {self.module} "
                f"{self.target or '(no target)'} {self.mode}>")

