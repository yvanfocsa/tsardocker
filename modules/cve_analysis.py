import shlex

MODULE = {
    "name":        "CVE Analysis – IA",
    "description": "Extraction de CVE et analyse via IA interne",
    "category":    "Reporting",
    "hidden":      False,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "exemple.com ou 1.2.3.4", "required": True},
        {"name": "source", "type": "select", "choices": ["nuclei", "openvas", "searchsploit"], "default": "nuclei"},
    ],
    "cmd": lambda p: [
        "bash", "-c",
        " && ".join([
            # 1) Générer un rapport JSON
            f"{p['source']} -json -u {shlex.quote(p['target'])} > findings.json || true",
            # 2) Extraire CVE
            "cves=$(jq -r '.[] | .info.cve[]? // empty' findings.json | sort -u) || true",
            # 3) Pour chaque CVE, interroger l’IA interne
            (
                "for cve in $cves; do "
                "echo '---'; echo \"Analyse $cve:\"; "
                f"curl -s -X POST http://localhost:5373/cve/analyze -H 'Content-Type: application/json' -d '{{\"cve\":\"'$cve'\"}}' | jq -r '.analysis'; "
                "done"
            )
        ])
    ],
}
