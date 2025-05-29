import shlex

MODULE = {
    "name": "Vuln Assessment",
    "description": "nuclei, nikto",
    "category": "Vulnerability",
    "hidden":    True,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "example.com"},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"]},
    ],
    "cmd": lambda params: [
        "bash", "-c",
        " && ".join(
            [
                "nuclei -u {}".format(shlex.quote(params.get("target", ""))),
                "nikto -h {}".format(shlex.quote(params.get("target", ""))),
            ]
        )
    ],
}
