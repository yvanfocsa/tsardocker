# modules/reporting_global.py
import json

MODULE = {
    "name":        "Rapport – Génération",
    "description": "génère le rapport PDF modulable et chiffré",
    "category":    "Reporting",
    "hidden":      False,
    "schema": [
        {"name": "sections", "type": "multiselect", "choices": ["recon", "scan", "vuln", "exploit", "cve"]}
    ],
    "cmd": lambda p: [
        "bash", "-c",
        f"echo 'Génération du rapport pour sections: {shlex.quote(json.dumps(p.get('sections', [])))}'"
    ],
}
