# web/app/routes.py

import datetime
import os
import socket
from io import BytesIO

import docker
import psutil
import requests
import feedparser
from flask import (
    Blueprint, Response, abort, current_app, jsonify, redirect,
    render_template, request, send_file, session, stream_with_context,
    url_for,
)
from flask_login import (
    LoginManager, UserMixin, current_user, login_required,
    login_user, logout_user,
)

from . import db
from .modules import MODULES, get_categories
from .models import ScanLog, Report
from .tasks import run_job
from .pdf_crypto import decrypt

# Import Blueprint CVE Analysis
from .cve_ai import bp_cve

# Blueprint principal
bp = Blueprint("routes", __name__)
login_manager = LoginManager()
login_manager.login_view = "routes.login"

# ─────────── USER SESSION ───────────
class User(UserMixin):
    def __init__(self, sub: str, name: str):
        self.id = sub
        self.sub = sub
        self.name = name

@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    data = session.get("user")
    if not data:
        return None
    return User(data["sub"], data.get("name", data.get("email", "")))

# ─────────── HELPERS ───────────
def _get_ips() -> tuple[str, str]:
    priv = socket.gethostbyname(socket.gethostname())
    try:
        pub = requests.get("https://api.ipify.org", timeout=2).text
    except requests.RequestException:
        pub = "n/a"
    return pub, priv

# ─────────── AUTH0 ───────────
@bp.route("/login")
def login():
    redirect_uri = url_for("routes.callback", _external=True)
    return current_app.oauth.auth0.authorize_redirect(
        redirect_uri=redirect_uri,
        audience=current_app.config["AUTH0_AUDIENCE"],
    )

@bp.route("/auth/callback")
def callback():
    token = current_app.oauth.auth0.authorize_access_token()
    user = current_app.oauth.auth0.parse_id_token(token, nonce=token.get("nonce"))
    session["user"] = dict(user)
    login_user(User(user["sub"], user.get("name", user.get("email", ""))))
    return redirect(url_for("routes.index"))

@bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(
        f'https://{current_app.config["AUTH0_DOMAIN"]}/v2/logout?'
        f'returnTo={url_for("routes.index", _external=True)}&'
        f'client_id={current_app.config["AUTH0_CLIENT_ID"]}'
    )

# ─────────── SYSTEM METRICS ───────────
@bp.route("/metrics/ram")
@login_required
def metrics_ram():
    mem = psutil.virtual_memory()
    used = (mem.total - mem.available) // (1024**2)
    total = mem.total // (1024**2)
    return f"{used} MiB / {total} MiB"

# ─────────── DASHBOARD ───────────
@bp.route("/")
@login_required
def index():
    pub_ip, priv_ip = _get_ips()
    mem = psutil.virtual_memory()
    ram = f"{(mem.total - mem.available) // 1024**2} MiB / {mem.total // 1024**2} MiB"
    metrics = {
        "RAM utilisée": ram,
        "IP publique": pub_ip,
        "IP privée": priv_ip,
    }
    favoris = [m for m in MODULES if m["name"] in session.get("favorites", [])]
    logs = (
        ScanLog.query
        .filter_by(user_sub=current_user.sub)
        .order_by(ScanLog.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "dashboard.html",
        metrics=metrics,
        favoris=favoris,
        logs=logs,
    )

# ─────────── MODULES LIST ───────────
@bp.route("/modules")
@login_required
def modules_home():
    return render_template("modules.html", cats=get_categories())

# ─────────── FAVORITES ───────────
@bp.route("/modules/<name>/favorite", methods=["POST"])
@login_required
def toggle_favorite(name: str):
    fav = session.setdefault("favorites", [])
    if name in fav:
        fav.remove(name)
    else:
        fav.append(name)
    session.modified = True
    star = "★" if name in fav else "☆"
    return (
        f'<button hx-post="{url_for("routes.toggle_favorite", name=name)}" '
        'hx-swap="outerHTML" class="fav-btn text-2xl">'
        f'{star}</button>',
        200,
        {"Content-Type": "text/html"},
    )

# ─────────── LIVE TERMINAL ───────────
@bp.route("/modules/<name>/terminal")
@login_required
def module_live(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)
    return render_template("module_live.html", mod=mod)

@bp.route("/modules/<name>/stream")
@login_required
def module_stream(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)
    target = request.args.get("target", "").strip()
    mode = request.args.get("mode", "quick")
    cmd = mod["cmd"]({"target": target, "mode": mode})
    cli = docker.from_env()
    tbx = os.getenv("TOOLBOX_CONTAINER", "tsar_full-toolbox-1")
    try:
        c = cli.containers.get(tbx)
    except docker.errors.NotFound:
        return Response("data: ERREUR: conteneur introuvable\n\n", mimetype="text/event-stream")
    exec_id = cli.api.exec_create(c.id, cmd, tty=False)["Id"]
    stream = cli.api.exec_start(exec_id, stream=True, demux=True)
    db.session.add(ScanLog(
        user_sub=current_user.sub,
        module=name,
        target=target or None,
        mode=mode,
    ))
    db.session.commit()

    @stream_with_context
    def events():
        yield f"data: ▶ Exécution : {' '.join(cmd)}\n\n"
        for out, err in stream:
            chunk = (out or err).decode(errors="ignore")
            for line in chunk.splitlines():
                yield f"data: {line}\n\n"
        yield "data: * Fin du flux.\n\n"

    return current_app.response_class(events(), mimetype="text/event-stream")

# ─────────── CLASSIC FORM ───────────
@bp.route("/modules/<name>")
@login_required
def module_form(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)
    return render_template("module_form.html", mod=mod)

@bp.route("/modules/<name>/run", methods=["POST"])
@login_required
def module_run(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        return jsonify({"error": "module not found"}), 404
    params = {f["name"]: request.form.get(f["name"], "") for f in mod["schema"]}
    job_id = run_job(mod, params, current_user.sub)
    return jsonify({"job_id": job_id})

# ─────────── PDF REPORTS ───────────
@bp.route("/reports")
@login_required
def reports():
    reps = (
        Report.query
        .filter_by(user_sub=current_user.sub)
        .order_by(Report.created_at.desc())
        .all()
    )
    return render_template("reports.html", reports=reps)

@bp.route("/reports/<int:rid>")
@login_required
def download_report(rid: int):
    rep = Report.query.get_or_404(rid)
    if rep.user_sub != current_user.sub:
        abort(403)
    pdf = decrypt(rep.pdf_data)
    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name=rep.filename,
        mimetype="application/pdf",
    )

# ─────────── FLUX RSS VEILLE ───────────
@bp.route("/veille")
@login_required
def veille():
    rss_url = "https://cyberveille.curated.co/issues.rss"
    feed = feedparser.parse(rss_url)
    entries = feed.entries[:20]
    return render_template("veille.html", entries=entries)

# Dans create_app() (web/app/__init__.py), n’oublie pas :
#   app.register_blueprint(bp)
#   app.register_blueprint(bp_cve)

