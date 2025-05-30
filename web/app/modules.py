# web/app/modules.py

"""
Chargement dynamique des modules “outils” depuis tsar_full/modules
Les MODULES marqués hidden=True sont ignorés,
et les doublons de nom sont automatiquement filtrés.
"""

import importlib.util as iutil
import logging
import pathlib
from typing import Dict, List

MODULES: List[dict] = []  # utilisé par routes.py/get_categories()


def load_modules() -> None:
    """
    Parcourt tsar_full/modules/*.py, importe chaque module, récupère sa variable MODULE (dict),
    et l’ajoute à MODULES si elle n’est pas cachée et n’existe pas déjà.
    """
    # Chemin vers tsar_full/modules
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


def get_categories() -> Dict[str, List[dict]]:
    """
    Retourne { catégorie: [MODULES triés par name] } pour affichage.
    """
    cats: Dict[str, List[dict]] = {}
    for mod in MODULES:
        cats.setdefault(mod["category"], []).append(mod)

    # tri alphabétique dans chaque catégorie
    for lst in cats.values():
        lst.sort(key=lambda x: x["name"].lower())
    return cats

