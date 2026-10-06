# Catalogue Microduck

Les pièces imprimables pour **[Microduck](https://github.com/pollen-robotics/microduck)** (Pollen Robotics), telles
qu'elles apparaissent dans la **marketplace de l'application Microduck** (icône sac en haut à droite).

**Exemple complet** : [`pieces/coque-superieure-origine/`](pieces/coque-superieure-origine) (la coque de tête
d'origine : fiche, deux photos, aperçu 3D). Pour rester uniforme, pars de ce dossier.

Ce dépôt ne contient **pas** les fichiers à imprimer : chaque pièce renvoie vers sa page sur
[Printables](https://www.printables.com) ou [Cults](https://cults3d.com), où on la télécharge. Il contient juste une
fiche, des photos et, si tu veux, un STL d'aperçu pour l'essayer en 3D sur son Microduck dans l'appli.

Envie de proposer ta pièce ? Voir [`CONTRIBUTING.md`](CONTRIBUTING.md) (pull request, ou simple *issue*).

## Ajouter une pièce (depuis github.com, même sur téléphone)

1. **Créer la fiche** : bouton **Add file → Create new file**. Dans le nom, tape `pieces/casque-viking/fiche.toml`
   (le `/` crée le dossier). Colle le contenu de [`pieces/_modele/fiche.toml`](pieces/_modele/fiche.toml) (tous les champs expliqués) ou de
   la fiche de l'exemple, remplis-le,
   puis **Commit changes**.
2. **Ajouter les photos** (et l'aperçu) : ouvre le dossier `pieces/casque-viking/`, **Add file → Upload files**, glisse
   tes photos (jpg, png ou webp ; la première par ordre alphabétique sert de couverture : numérote-les comme
   l'exemple, `1-….jpg`, `2-….jpg`) et, si tu veux, `apercu.stl`. **Commit changes**.
   Photos conseillées : 4:3 (ex. 1200 × 900), fond clair, la pièce seule puis montée sur le Microduck.
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

## Prêt à imprimer (G-code)

Une pièce peut fournir un G-code **déjà tranché** pour une imprimante précise. Pose le fichier `.bgcode` ou `.gcode`
dans le dossier de la pièce, puis déclare-le dans la fiche avec un bloc `[[fichier]]` : nom du fichier, imprimante,
matériau (voir `pieces/_modele/fiche.toml`).

Dans l'application, un bouton **Envoyer à l'imprimante** apparaît sur la pièce. Le téléphone télécharge le fichier
ici, puis le canard le dépose sur ta Prusa du réseau local (PrusaLink). Il peut aussi lancer l'impression.

- Le canard ne va jamais sur Internet.
- La clé API de l'imprimante reste sur le canard.
- Taille maximale : 64 Mo par fichier.

## Chorégraphies

Les tours composés dans le studio de l'application se partagent ici, un fichier par chorégraphie :
`choregraphies/<nom>.json`. Pour en proposer une :

1. Dans le studio, utilise **Exporter** pour obtenir le fichier.
2. Ajoute-le dans le dossier `choregraphies/` (voir `choregraphies/coucou.json`).

Elles apparaissent dans le studio, rubrique **Du catalogue**. Seuls les gestes, les sons de canard, les positions de
tête, s'asseoir et les pauses sont acceptés, comme dans l'appli.

## Fonctionnement

`outils/construire.py` lit les fiches et écrit `catalogue.json` ; `.github/workflows/catalogue.yml` le lance à chaque
envoi. L'application lit `catalogue.json`, les photos et les aperçus directement ici (depuis le téléphone : le canard,
lui, n'en a pas besoin).
