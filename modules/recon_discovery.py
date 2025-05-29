import shlex

MODULE = {
    "name": "Recon – Discovery",
    "description": "subfinder, whois, dnsenum",
    "category": "Recon",
    "hidden":    True,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "example.com"},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"]},
    ],
    "cmd": lambda params: [
        "bash", "-c",
        " && ".join(
            [
                " ".join(shlex.quote(arg) for arg in c)
                for c in [
                    ["subfinder", "-d", params.get("target", "")],
                    ["whois", params.get("target", "")],
                    ["dnsenum", params.get("target", "")],
                ]
            ]
        )
    ],
    # hidden: False (par défaut)
}
