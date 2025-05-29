# web/modules/whois.py
MODULE = {
    "name": "whois",
    "binary": "whois",
    "category": "Recon",
    "hidden":    True,
    "description": "WHOIS lookup",
    "schema": [                      # ← inutilisé dans le live-terminal
        {"name": "target", "label": "Domaine/IP", "type": "text"},
    ],
    "cmd": lambda p: ["whois", p.get("target", "").strip()],
}

