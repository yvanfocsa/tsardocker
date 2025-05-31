# modules/reporting_global.py
import json
import shlex  # Pour shlex.quote

# Import des modules outils
from modules.recon_global    import MODULE as _mod_recon
from modules.scanning_global import MODULE as _mod_scan
from modules.vuln_global     import MODULE as _mod_vuln
from modules.exploit_global  import MODULE as _mod_exploit
from modules.cve_analysis    import MODULE as _mod_cve

# Mapping des clés de section vers les modules
MODULE_MAP = {
    "recon":   _mod_recon,
    "scan":    _mod_scan,
    "vuln":    _mod_vuln,
    "exploit": _mod_exploit,
    "cve":     _mod_cve,
}

MODULE = {
    "name":        "Rapport – Génération",
    "description": "génère le rapport PDF modulable et chiffré",
    "category":    "Reporting",
    "binary":      "rapport",
    "hidden":      False,
    "schema": [
        {"name": "target",   "type": "string",      "placeholder": "exemple.com ou 1.2.3.4", "required": True},
        {"name": "sections", "type": "multiselect", "choices": list(MODULE_MAP.keys())}
    ],
    "cmd": lambda p: [
        "bash", "-c",
        # Enchaîne les commandes de chaque module sélectionné
        " && ".join(
            " ".join(shlex.quote(str(part)) for part in MODULE_MAP[sec]["cmd"]({
                "target": p.get("target", ""),
                "mode":   p.get("mode", "quick")
            }))
            for sec in p.get("sections", [])
            if sec in MODULE_MAP
        ) or "echo 'Aucune section sélectionnée'"
    ],
}

