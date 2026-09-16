# Données sources

Les fichiers de données **ne sont pas versionnés** (voir `.gitignore`) : ce sont des
exports publics, volumineux et régulièrement mis à jour à la source. Seul ce fichier
est suivi par git. Les démos publiées dans `demos/` embarquent déjà les données dont
elles ont besoin ; ce répertoire n'est nécessaire que pour **reconstruire** une démo
avec `src/build_<nom>.py`.

Arborescence attendue par les scripts de construction :

```
data/odisse/*.csv      exports Odissé, tels que téléchargés (UTF-8 avec BOM, séparateur « , »)
data/geo/*.geojson     contours départementaux, copies exactes de france-geojson
```

## `data/odisse/` — Santé publique France, plateforme Odissé

Portail : <https://odisse.santepubliquefrance.fr>. Chaque jeu de données a une page
`https://odisse.santepubliquefrance.fr/explore/dataset/<identifiant>/`, dont l'onglet
« Export » fournit le CSV. Les fichiers sont conservés **sans modification** ; leur nom
local est celui de l'identifiant du jeu de données.

| Fichier | Identifiant du jeu de données | Contenu | Couverture de l'export utilisé |
|---|---|---|---|
| `infection-invasive-a-meningocoque-notifications.csv` | `infection-invasive-a-meningocoque-notifications` | Déclaration obligatoire des infections invasives à méningocoque : nombre de cas, taux de notification et population, par année, département et sérogroupe (`Tous types`, `B`, `C`, `W`, `Y`) | 1995-2025, 15 565 lignes, 9 colonnes |
| `couvertures-vaccinales-archives-departement.csv` | `couvertures-vaccinales-archives-departement` | Couvertures vaccinales départementales archivées (DTP, coqueluche, Hib, méningocoque C de 24 mois à 20-24 ans) | 2004-2024, 2 100 lignes, 16 colonnes |
| `couvertures-vaccinales-des-adolescent-et-adultes-departement.csv` | `couvertures-vaccinales-des-adolescent-et-adultes-departement` | Couvertures vaccinales départementales des adolescents et adultes (HPV, grippe, Covid-19, méningocoques ACWY 11-14 / 15 / 15-24 ans, DTP, coqueluche) | 2011-2025, 1 515 lignes, 25 colonnes |

Colonnes réellement lues par `src/build_meningocoque.py` : `Année`, `Département`,
`Département Code`, `Région`, `Région Code`, `Méningocoque`, `Nombre de cas`,
`Population` pour les notifications ; `Année`, `Département Code` et les colonnes
`Méningocoque C …` / `Méningocoques ACWY …` pour les couvertures. Les lignes de
`Département Code` égal à `0` (total France) sont écartées à la construction.

Licence : Licence Ouverte / Open Licence (Etalab), Santé publique France.

Les exports étant mis à jour à la source, un nouveau téléchargement peut allonger la
plage d'années ou ajouter des colonnes ; la démo reconstruite s'y adapte (les années et
les indicateurs disponibles sont déduits des fichiers).

## `data/geo/` — contours départementaux (france-geojson)

Copies exactes (vérifiées par somme de contrôle) de fichiers du projet
[france-geojson](https://github.com/gregoiredavid/france-geojson) de Grégoire David,
renommées localement. À retélécharger avec :

```bash
mkdir -p data/geo
B=https://raw.githubusercontent.com/gregoiredavid/france-geojson/master
curl -o data/geo/departements-version-simplifiee.geojson "$B/departements-version-simplifiee.geojson"
curl -o data/geo/dom-971.geojson "$B/departements/971-guadeloupe/departement-971-guadeloupe.geojson"
curl -o data/geo/dom-972.geojson "$B/departements/972-martinique/departement-972-martinique.geojson"
curl -o data/geo/dom-973.geojson "$B/departements/973-guyane/departement-973-guyane.geojson"
curl -o data/geo/dom-974.geojson "$B/departements/974-la-reunion/departement-974-la-reunion.geojson"
curl -o data/geo/dom-976.geojson "$B/departements/976-mayotte/departement-976-mayotte.geojson"
```

| Fichier local | Chemin amont | Type GeoJSON |
|---|---|---|
| `departements-version-simplifiee.geojson` | `departements-version-simplifiee.geojson` | `FeatureCollection`, 96 départements de métropole (Corse comprise), propriétés `code` et `nom` |
| `dom-971.geojson` | `departements/971-guadeloupe/departement-971-guadeloupe.geojson` | `Feature` unique, Guadeloupe |
| `dom-972.geojson` | `departements/972-martinique/departement-972-martinique.geojson` | `Feature` unique, Martinique |
| `dom-973.geojson` | `departements/973-guyane/departement-973-guyane.geojson` | `Feature` unique, Guyane |
| `dom-974.geojson` | `departements/974-la-reunion/departement-974-la-reunion.geojson` | `Feature` unique, La Réunion |
| `dom-976.geojson` | `departements/976-mayotte/departement-976-mayotte.geojson` | `Feature` unique, Mayotte |

Les contours de métropole sont déjà simplifiés en amont ; `build_meningocoque.py` les
simplifie encore (Douglas-Peucker) et place les DOM en cartouches. La collection de
métropole ne contient pas les DOM, d'où les cinq fichiers séparés.

Licence : Licence Ouverte / Open Licence (Etalab) — voir le dépôt france-geojson.
