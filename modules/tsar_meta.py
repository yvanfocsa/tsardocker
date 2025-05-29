import shlex

MODULE = {
    "name": "TSAR – Tactical Security Automation & Recon",
    "description": "ubfinder, whois, dnsenum, nmap, nuclei, nikto, searchsploit",
    "category": "META",
    "hidden":    True,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "example.com"},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"]},
    ],
    "cmd": lambda params: [
        "bash", "-c",
        " && ".join(
            [
                " ".join(shlex.quote(a) for a in (
                    ["subfinder", "-d", params.get("target", "")],
                    ["whois", params.get("target", "")],
                    ["dnsenum", params.get("target", "")],
                    ["nmap", "-sS", "-T4", "--top-ports", "100", params.get("target", "")] if params.get("mode") == "quick"
                    else ["nmap", "-sS", "-sV", "-sC", "-O", "-T4", "-Pn", "--version-intensity", "9", params.get("target", "")],
                    ["nuclei", "-u", params.get("target", "")],
                    ["nikto", "-h", params.get("target", "")],
                    ["searchsploit", params.get("target", "")],
                ))
            ]
        )
    ],
}
