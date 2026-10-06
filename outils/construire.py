#!/usr/bin/env python3
"""Fabrique catalogue.json a partir des fiches pieces/<dossier>/fiche.toml (lance par GitHub Actions a chaque envoi).

    python3 outils/construire.py            # ecrit catalogue.json
    python3 outils/construire.py --verifier # verifie seulement (erreur si une fiche est fausse)
"""
import json
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

RACINE = Path(__file__).resolve().parents[1]
DEPOT = "RaphaelGrj/microduck-catalogue"
BRUT = f"https://raw.githubusercontent.com/{DEPOT}/main/"
CATEGORIES = ["tête", "corps", "pieds", "accessoire", "support", "autre"]
IMAGES = {".jpg", ".jpeg", ".png", ".webp"}
APERCU_MAX = 8 * 1024 * 1024
GCODE_MAX = 64 * 1024 * 1024          # (le canard refuse au-dela)
# choregraphies : ce que le studio de l'application sait jouer (choregraphies.py de microduck-brain)
SONS = {"alarm", "greet", "inquire", "peck", "chirp", "coo", "wheee"}
# schemas de couleurs : groupes de pieces imprimables du design space (interface/design/microduck.json)
GROUPES = {"dessus_tete", "dessous_tete", "face", "bec", "bec_souple", "oeil", "coques", "chassis", "cou", "hanches",
           "cuisses", "jambes", "pieds", "semelles", "support_batterie"}
GESTES = {"baillement", "content", "curieux", "ebouriffe", "eternuement", "etirement", "fatigue", "fier", "gene",
          "lissage", "non", "oui", "surpris"}
# pieces d'origine imprimables qu'une piece du catalogue peut remplacer (noms des STL officiels de microduck_rl)
REMPLACABLES = {
    "top_head_shell": "Dessus de la tête", "bottom_head_shell": "Dessous de la tête", "face_part": "Face",
    "jaw": "Bec", "jaw_soft": "Bec souple", "soft_mouth_top": "Bec souple (haut)", "noenoeil": "Tour de l'œil",
    "left_shell": "Coque gauche", "right_shell": "Coque droite", "trunk_base": "Châssis",
    "motor_support": "Support moteur", "yaw2roll": "Pièce de hanche", "yaw_roll_motion": "Pièce de hanche (rotation)",
    "bearing_roll": "Roulement de hanche", "neck": "Cou", "neck_pitch": "Cou (tangage)", "hip_l": "Hanche",
    "upper_leg_left": "Cuisse gauche", "upper_leg_right": "Cuisse droite", "leg": "Jambe",
    "upper_leg_rigidity_plate": "Plaque de cuisse", "foot_left": "Pied gauche", "foot_right": "Pied droit",
    "ankle_left": "Cheville gauche", "ankle_right": "Cheville droite", "sole_left": "Semelle gauche",
    "sole_right": "Semelle droite", "power_support": "Support de batterie", "banana_pcb_locker": "Verrou de carte",
}


def lien(url, champ, erreurs, dossier):
    if url is None:
        return None
    u = urlparse(str(url))
    if u.scheme != "https" or not u.netloc:
        erreurs.append(f"{dossier}: {champ} doit etre une adresse https://")
        return None
    return str(url)


def fiche(dossier, erreurs):
    try:
        f = tomllib.loads((dossier / "fiche.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        erreurs.append(f"{dossier.name}: fiche.toml illisible ({e})")
        return None
    if f.get("publie", True) is False:
        return None
    nom = str(f.get("nom") or "").strip()
    if not nom:
        erreurs.append(f"{dossier.name}: « nom » manquant")
    categorie = f.get("categorie", "autre")
    if categorie not in CATEGORIES:
        erreurs.append(f"{dossier.name}: categorie « {categorie} » inconnue ({', '.join(CATEGORIES)})")
    liens = {k: lien(f.get(k), k, erreurs, dossier.name) for k in ("printables", "cults", "autre")}
    liens = {k: v for k, v in liens.items() if v}
    if not liens and not f.get("bientot"):
        erreurs.append(f"{dossier.name}: il faut un lien (printables, cults ou autre), ou « bientot = true »")
    base = BRUT + "pieces/" + quote(dossier.name) + "/"
    photos = sorted(p.name for p in dossier.iterdir() if p.suffix.lower() in IMAGES)
    remplace = f.get("remplace")
    if remplace is not None and remplace not in REMPLACABLES:
        erreurs.append(f"{dossier.name}: remplace = « {remplace} » inconnu (voir la liste dans le README)")
    apercu = f.get("apercu")
    if apercu is not None:
        chemin = dossier / str(apercu)
        if not chemin.is_file() or chemin.suffix.lower() != ".stl":
            erreurs.append(f"{dossier.name}: apercu « {apercu} » introuvable (un fichier .stl de ce dossier)")
        elif chemin.stat().st_size > APERCU_MAX:
            erreurs.append(f"{dossier.name}: apercu trop gros (8 Mo au plus : allege-le)")
        if remplace is None:
            erreurs.append(f"{dossier.name}: un apercu demande « remplace » (la piece d'origine qu'il remplace)")
    fichiers = []
    for k, x in enumerate(f.get("fichier") or []):
        chemin = dossier / str(x.get("nom", ""))
        if not chemin.is_file() or chemin.suffix.lower() not in (".bgcode", ".gcode"):
            erreurs.append(f"{dossier.name}: fichier n°{k + 1} « {x.get('nom')} » introuvable (.bgcode ou .gcode de ce dossier)")
        elif chemin.stat().st_size > GCODE_MAX:
            erreurs.append(f"{dossier.name}: {x.get('nom')} trop gros (64 Mo au plus)")
        elif not str(x.get("imprimante") or "").strip():
            erreurs.append(f"{dossier.name}: fichier « {x.get('nom')} » : « imprimante » manquante (ex. Prusa MK4S)")
        else:
            fichiers.append({"nom": chemin.name, "imprimante": str(x["imprimante"]).strip(), "url": base + quote(chemin.name),
                             "materiau": x.get("materiau"), "octets": chemin.stat().st_size})
    return {
        "id": dossier.name, "nom": nom, "description": str(f.get("description") or "").strip(),
        "categorie": categorie, "auteur": f.get("auteur"), "licence": f.get("licence"),
        "impression": {k: f[k] for k in ("materiau", "temps", "filament_g", "supports") if k in f},
        "liens": liens, "bientot": bool(f.get("bientot")) and not liens,
        "photos": [base + quote(p) for p in photos],
        "remplace": remplace, "remplace_nom": REMPLACABLES.get(remplace),
        "apercu": base + quote(str(apercu)) if apercu else None,
        "ajoute": str(f.get("ajoute")) if f.get("ajoute") else None,
        "fichiers": fichiers,
    }


def schema(chemin, erreurs):
    """schemas/<id>.json : {"nom", "auteur", "description", "couleurs": {groupe: "#rrggbb"}} (export du design space)."""
    try:
        s = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        erreurs.append(f"{chemin.name}: illisible ({e})")
        return None
    if isinstance(s, dict) and isinstance(s.get("schema"), dict):
        s = {**s["schema"], **{k: s[k] for k in ("auteur", "description") if k in s}}
    nom = str((s or {}).get("nom") or "").strip()[:40]
    couleurs = (s or {}).get("couleurs") if isinstance((s or {}).get("couleurs"), dict) else {}
    faux = [g for g, v in couleurs.items() if g not in GROUPES or not re.fullmatch(r"#[0-9a-fA-F]{6}", str(v))]
    if not nom or not couleurs or faux:
        erreurs.append(f"{chemin.name}: « nom » et « couleurs » {{groupe: #rrggbb}} attendus" + (f" (inconnu : {faux})" if faux else ""))
        return None
    return {"id": chemin.stem, "nom": nom, "auteur": s.get("auteur"), "description": str(s.get("description") or "").strip(),
            "couleurs": {g: v.lower() for g, v in couleurs.items()}}


def choregraphie(chemin, erreurs):
    """choregraphies/<id>.json : {"nom", "auteur", "description", "etapes": [...]} (format de l'export de l'appli)."""
    try:
        c = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        erreurs.append(f"{chemin.name}: illisible ({e})")
        return None
    c = c.get("choregraphie", c) if isinstance(c, dict) else {}
    nom = str(c.get("nom") or "").strip()[:40]
    etapes = c.get("etapes") if isinstance(c.get("etapes"), list) else []
    if not nom or not etapes or len(etapes) > 40:
        erreurs.append(f"{chemin.name}: « nom » et 1 a 40 « etapes » attendus")
        return None
    for k, e in enumerate(etapes):
        t = e.get("type") if isinstance(e, dict) else None
        if t not in ("tete", "son", "geste", "assis", "pause") or (t == "son" and e.get("son") not in SONS) \
                or (t == "geste" and e.get("geste") not in GESTES):
            erreurs.append(f"{chemin.name}: etape n°{k + 1} inconnue ({e})")
            return None
    return {"id": chemin.stem, "nom": nom, "auteur": c.get("auteur"), "description": str(c.get("description") or "").strip(),
            "etapes": etapes}


def construire():
    erreurs, pieces = [], []
    for dossier in sorted((RACINE / "pieces").iterdir()):
        if dossier.is_dir() and not dossier.name.startswith(("_", ".")):
            p = fiche(dossier, erreurs)
            if p:
                pieces.append(p)
    choregraphies = []
    if (RACINE / "choregraphies").is_dir():
        for chemin in sorted((RACINE / "choregraphies").glob("*.json")):
            c = choregraphie(chemin, erreurs)
            if c:
                choregraphies.append(c)
    schemas = []
    if (RACINE / "schemas").is_dir():
        for chemin in sorted((RACINE / "schemas").glob("*.json")):
            sc = schema(chemin, erreurs)
            if sc:
                schemas.append(sc)
    return {"version": 1, "depot": DEPOT, "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            "pieces": pieces, "choregraphies": choregraphies, "schemas": schemas}, erreurs


def main():
    catalogue, erreurs = construire()
    for e in erreurs:
        print("ERREUR", e)
    if erreurs:
        sys.exit(1)
    print(f"{len(catalogue['pieces'])} piece(s), {len(catalogue['choregraphies'])} choregraphie(s), "
          f"{len(catalogue['schemas'])} schema(s)")
    if "--verifier" not in sys.argv:
        ancien = {}
        try:
            ancien = json.loads((RACINE / "catalogue.json").read_text())
        except (OSError, ValueError):
            pass
        if {**ancien, "maj": None} != {**catalogue, "maj": None}:     # ne change la date que si le contenu change
            (RACINE / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
