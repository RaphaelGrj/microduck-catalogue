#!/usr/bin/env python3
"""Fabrique catalogue.json a partir des fiches pieces/<dossier>/fiche.toml (lance par GitHub Actions a chaque envoi).

    python3 outils/construire.py            # ecrit catalogue.json
    python3 outils/construire.py --verifier # verifie seulement (erreur si une fiche est fausse)
"""
import json
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
    return {
        "id": dossier.name, "nom": nom, "description": str(f.get("description") or "").strip(),
        "categorie": categorie, "auteur": f.get("auteur"), "licence": f.get("licence"),
        "impression": {k: f[k] for k in ("materiau", "temps", "filament_g", "supports") if k in f},
        "liens": liens, "bientot": bool(f.get("bientot")) and not liens,
        "photos": [base + quote(p) for p in photos],
        "remplace": remplace, "remplace_nom": REMPLACABLES.get(remplace),
        "apercu": base + quote(str(apercu)) if apercu else None,
        "ajoute": str(f.get("ajoute")) if f.get("ajoute") else None,
    }


def construire():
    erreurs, pieces = [], []
    for dossier in sorted((RACINE / "pieces").iterdir()):
        if dossier.is_dir() and not dossier.name.startswith(("_", ".")):
            p = fiche(dossier, erreurs)
            if p:
                pieces.append(p)
    return {"version": 1, "depot": DEPOT, "maj": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            "pieces": pieces}, erreurs


def main():
    catalogue, erreurs = construire()
    for e in erreurs:
        print("ERREUR", e)
    if erreurs:
        sys.exit(1)
    print(f"{len(catalogue['pieces'])} piece(s)")
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
