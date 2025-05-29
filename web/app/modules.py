# web/app/modules.py

"""
Chargement dynamique des modules “outils” + 6 méta-modules français :

  • Collecte d’informations     (subfinder, whois, dnsenum)
  • Cartographie réseau         (nmap)
  • Analyse des vulnérabilités  (nuclei, nikto)
  • Attaque active              (searchsploit)
  • OSINT                       (theHarvester, shodan)
  • Rapports                    (export des résultats)

Les MODULES marqués hidden=True sont ignorés,
et les doublons de nom sont automatiquement filtrés.
"""

import importlib.util as iutil
import logging
import pathlib
import shlex
from typing import Dict, List

MODULES: List[dict] = []  # exporté et utilisé par routes.py/get_categories()


def load_modules() -> None:
    """
    Parcourt web/modules/*.py, importe chaque module, récupère sa variable MODULE (dict),
    et l’ajoute à MODULES si elle n’est pas cachée et n’existe pas déjà.
    """
    root = pathlib.Path(__file__).resolve().parents[1] / "modules"
    if not root.exists():
        logging.warning("Dossier modules introuvable : %s", root)
        return

    for file in root.rglob("*.py"):
        spec = iutil.spec_from_file_location(f"tsar_mod.{file.stem}", file)
        mod = iutil.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as err:
            logging.error("Erreur import %s : %s", file.name, err, exc_info=True)
            continue

        meta = getattr(mod, "MODULE", None)
        if not isinstance(meta, dict):
            continue

        # ignore les modules cachés
        if meta.get("hidden", False):
            continue

        # filtre les doublons de nom
        if any(m["name"] == meta["name"] for m in MODULES):
            logging.warning("Module %s déjà chargé, on l’ignore", meta["name"])
            continue

        MODULES.append(meta)

    _inject_meta_modules()


def _inject_meta_modules() -> None:
    """
    Crée 6 méta-modules qui enchaînent les outils principaux pour chaque partie.
    """
    def tool(name: str) -> dict:
        return next(m for m in MODULES if m["name"] == name)

    def chain(label: str, names: List[str], category: str) -> dict:
        def _cmd(params: dict) -> List[str]:
            cmds = [tool(n)["cmd"](params) for n in names]
            joined = " && ".join(
                " ".join(shlex.quote(str(a)) for a in c)
                for c in cmds
            )
            return ["bash", "-c", joined]

        return {
            "name":        label,
            "description": f"",
            "category":    category,
            "binary":      "meta",
            "schema": [
                {"name": "target", "type": "string", "placeholder": "ex : example.com"},
                {"name": "mode",   "type": "select", "choices": ["quick", "full"]},
            ],
            "cmd": _cmd,
        }

    # listes d’outils existants (noms EXACTS de vos MODULES “outils”)
    recon_tools   = ["subfinder", "whois", "dnsenum"]
    scan_tools    = ["nmap"]
    vuln_tools    = ["nuclei", "nikto"]
    exploit_tools = ["searchsploit"]
    osint_tools   = ["theHarvester", "shodan"]   # à ajuster selon vos modules OSINT
    report_tools  = ["pdf_report"]               # module interne de génération de PDF

    MODULES.extend([
        chain("Reconnaissance",      recon_tools,    "Reconnaissance"),
        chain("Analyse",          scan_tools,     "Analyse"),
        chain("Vulnérabilités",   vuln_tools,     "Vulnérabilités"),
        chain("Exploitation",               exploit_tools,  "Exploitation"),
        chain("OSINT",                        osint_tools,    "OSINT"),
        chain("Rapports",                     report_tools,   "Rapports"),
    ])


def get_categories() -> Dict[str, List[dict]]:
    """
    Retourne { catégorie: [MODULES triés par name] } pour affichage.
    Les catégories apparaissent dans l’ordre d’injection ci-dessus.
    """
    cats: Dict[str, List[dict]] = {}
    for mod in MODULES:
        cats.setdefault(mod["category"], []).append(mod)

    # tri alphabétique dans chaque catégorie
    for lst in cats.values():
        lst.sort(key=lambda x: x["name"].lower())
    return cats

