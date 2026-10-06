# Catalogue Microduck

Les pièces imprimables pour **[Microduck](https://github.com/pollen-robotics/microduck)** (Pollen Robotics), telles
qu'elles apparaissent dans la **marketplace de l'application Microduck** (icône sac en haut à droite).

Ce dépôt ne contient **pas** les fichiers à imprimer : chaque pièce renvoie vers sa page sur
[Printables](https://www.printables.com) ou [Cults](https://cults3d.com), où on la télécharge. Il contient juste une
fiche, des photos et, si tu veux, un STL d'aperçu pour l'essayer en 3D sur son Microduck dans l'appli.

## Ajouter une pièce (depuis github.com, même sur téléphone)

1. **Créer la fiche** : bouton **Add file → Create new file**. Dans le nom, tape `pieces/casque-viking/fiche.toml`
   (le `/` crée le dossier). Colle le contenu de [`pieces/_modele/fiche.toml`](pieces/_modele/fiche.toml), remplis-le,
   puis **Commit changes**.
2. **Ajouter les photos** (et l'aperçu) : ouvre le dossier `pieces/casque-viking/`, **Add file → Upload files**, glisse
   tes photos (jpg, png ou webp ; la première par ordre alphabétique sert de couverture, ex. `1-face.jpg`) et, si tu
   veux, `apercu.stl`. **Commit changes**.
3. C'est tout. En une minute, le robot du dépôt (onglet **Actions**) vérifie la fiche et met `catalogue.json` à jour.
   L'appli le voit à la prochaine ouverture de la marketplace.

Si la coche de l'onglet Actions est rouge, une fiche est mal remplie : le message dit laquelle et pourquoi.

- **Brouillon** : `publie = false` dans la fiche la garde hors du catalogue.
- **Pas encore en ligne** : `bientot = true` à la place des liens.
- **Retirer une pièce** : supprime son dossier.

## La fiche

Tous les champs sont dans [`pieces/_modele/fiche.toml`](pieces/_modele/fiche.toml) : nom, description, catégorie
(`tête`, `corps`, `pieds`, `accessoire`, `support`, `autre`), auteur, licence, impression (matériau, temps, grammes,
supports), liens `printables` / `cults` / `autre`.

## « Essayer sur mon Microduck » (aperçu 3D)

Pour qu'une pièce se pose sur le Microduck 3D de l'appli :

- **Pars du STL d'origine** de la pièce que tu remplaces (dossier
  [`assets` du modèle officiel](https://github.com/pollen-robotics/microduck_rl/tree/main/src/mjlab_microduck/robot/microduck/assets)),
  et garde son repère (origine et axes) : ta pièce se pose alors exactement à sa place. Millimètres ou mètres : l'appli
  devine.
- Dans la fiche : `remplace = "<nom de la pièce d'origine>"` et `apercu = "apercu.stl"` (8 Mo au plus ; une version
  allégée suffit).

| `remplace` | Pièce d'origine |
|---|---|
| `top_head_shell` | Dessus de la tête |
| `bottom_head_shell` | Dessous de la tête |
| `face_part` | Face |
| `jaw` | Bec |
| `jaw_soft` | Bec souple |
| `soft_mouth_top` | Bec souple (haut) |
| `noenoeil` | Tour de l'œil |
| `left_shell` | Coque gauche |
| `right_shell` | Coque droite |
| `trunk_base` | Châssis |
| `motor_support` | Support moteur |
| `yaw2roll` | Pièce de hanche |
| `yaw_roll_motion` | Pièce de hanche (rotation) |
| `bearing_roll` | Roulement de hanche |
| `neck` | Cou |
| `neck_pitch` | Cou (tangage) |
| `hip_l` | Hanche |
| `upper_leg_left` | Cuisse gauche |
| `upper_leg_right` | Cuisse droite |
| `leg` | Jambe |
| `upper_leg_rigidity_plate` | Plaque de cuisse |
| `foot_left` | Pied gauche |
| `foot_right` | Pied droit |
| `ankle_left` | Cheville gauche |
| `ankle_right` | Cheville droite |
| `sole_left` | Semelle gauche |
| `sole_right` | Semelle droite |
| `power_support` | Support de batterie |
| `banana_pcb_locker` | Verrou de carte |

## Fonctionnement

`outils/construire.py` lit les fiches et écrit `catalogue.json` ; `.github/workflows/catalogue.yml` le lance à chaque
envoi. L'application lit `catalogue.json`, les photos et les aperçus directement ici (depuis le téléphone : le canard,
lui, n'en a pas besoin).
