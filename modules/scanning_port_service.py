import shlex

MODULE = {
    "name": "Scanning – Port & Service",
    "description": "nmap",
    "category": "Recon",
    "hidden":    True,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "example.com"},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"]},
    ],
    "cmd": lambda params: [
        "bash", "-c",
        " ".join(shlex.quote(arg) for arg in (
            ["nmap", "-sS", "-T4", "--top-ports", "100", params.get("target", "")] if params.get("mode") == "quick"
            else ["nmap", "-sS", "-sV", "-sC", "-O", "-T4", "-Pn", "--version-intensity", "9", params.get("target", "")]
        ))
    ],
}
