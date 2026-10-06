# Proposer une pièce au catalogue Microduck

Merci ! Toute pièce imprimable pour Microduck est la bienvenue : coques, accessoires, supports, pieds…

## Le plus simple : une demande de fusion (pull request)

1. **Fork** ce dépôt (bouton *Fork* en haut à droite).
2. Dans ton fork, crée `pieces/<nom-de-ta-piece>/fiche.toml` à partir de
   [`pieces/coque-superieure-origine/fiche.toml`](pieces/coque-superieure-origine/fiche.toml) (l'exemple complet) ou
   du [modèle commenté](pieces/_modele/fiche.toml).
3. Ajoute 1 à 4 photos (`1-….jpg`, `2-….jpg`, 4:3 conseillé, fond clair) et, si tu veux, `apercu.stl` pour
   « Essayer sur mon Microduck » (dessiné à partir du STL d'origine, même repère ; 8 Mo au plus).
4. Ouvre une **pull request**. Le robot vérifie la fiche (onglet *Checks*) ; une fois fusionnée, la pièce apparaît dans
   l'application.

## Sans GitHub

Ouvre une *issue* « Proposer une pièce » : nom, liens Printables / Cults, photos. On s'occupe de la fiche.

## Les règles

- **Le fichier à imprimer reste chez toi** : sur Printables, Cults ou un autre site. Ce dépôt ne contient que la fiche,
  les photos et l'aperçu.
- **Ta licence** : indique-la dans la fiche (`licence = "CC BY-NC 4.0"`…). Les pièces dérivées des fichiers de Pollen
  Robotics respectent leur licence (Apache-2.0).
- **Des photos de ta pièce** : pas de visuels pris ailleurs sans autorisation.
- Une pièce qui pourrait abîmer le robot (surcharge des servos, blocage d'un axe) doit le dire dans sa description.
