# modules/recon/nmap.py
"""
Nmap – deux profils :
 • quick : top-100 ports, détection de version légère (≈ 5–10 s)
 • full  : scan complet + scripts + OS detect (≈ 2 min)

Le “mode” apparaît comme liste déroulante dans le formulaire
ET comme paramètre automatique dans le terminal live.
"""
MODULE = {
    "name":        "nmap",
    "category":    "Recon",
    "hidden":    True,
    "description": "Scan réseau avec nmap",
    "binary":      "nmap",
    "schema": [
        {"name": "target", "label": "Cible", "type": "text",  "required": True},
        {"name": "mode",   "label": "Mode",
         "type": "select", "choices": ["quick", "full"], "default": "quick"},
    ],
    "cmd": lambda p: {
        "quick": ["nmap", "-sS", "-T4", "--top-ports", "100",         p["target"]],
        "full":  ["nmap", "-sS", "-sV", "-sC", "-O", "-T4", "-Pn",
                  "--version-intensity", "9",                         p["target"]],
    }[p["mode"]],
}

