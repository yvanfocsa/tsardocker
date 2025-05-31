# web/app/tasks.py
import os
import datetime
import docker

from .pdf import generate_report
from .pdf_crypto import encrypt
from . import db

# Client Docker connecté au socket /var/run/docker.sock (monté dans le service web)
client = docker.from_env()


def run_job(mod: dict, params: dict, user_sub: str) -> int:
    """
    Exécute la commande du module dans le conteneur toolbox,
    génère un PDF à partir du stdout, chiffre ce PDF et enregistre un Report.

    :param mod:     dict MODULE contenant name, binary, cmd, …
    :param params:  paramètres saisis par l’utilisateur
    :param user_sub: identifiant Auth0 de l’utilisateur
    :return:        ID du Report créé en base
    """
    # ── import local pour éviter un import cyclique avec routes.py ──
    from .models import Report

    # 1) Construire la commande shell à lancer (voir MODULE["cmd"])
    cmd = mod["cmd"](params)

    # 2) Récupérer le conteneur Kali (toolbox) et exécuter la commande
    container_name = os.environ.get("TOOLBOX_CONTAINER", "tsar_full-toolbox-1")
    try:
        exec_res = client.containers.get(container_name).exec_run(
            cmd,
            stdout=True,
            stderr=True,
        )
        output = exec_res.output.decode(errors="ignore")
    except Exception as exc:
        output = f"ERREUR: {exc!s}"

    # 3) Générer le rapport PDF (template HTML -> PDF via wkhtmltopdf)
    pdf_bytes = generate_report(
        "stdout_report.html",
        {
            "module":  mod,
            "params":  params,
            "output":  output,
            "date":    datetime.datetime.utcnow(),
        },
    )

    # 4) Chiffrer puis stocker dans la table reports
    cipher = encrypt(pdf_bytes)

    report = Report(
        user_sub=user_sub,
        filename=f"{mod['binary']}_{datetime.datetime.utcnow():%Y%m%d%H%M}.pdf",
        pdf_data=cipher,
    )
    db.session.add(report)
    db.session.commit()

    return report.id

