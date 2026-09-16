# sante_publique_demos

Démonstrations de visualisation construites sur les données ouvertes de Santé publique
France (plateforme Odissé). Chaque démo est **un seul fichier HTML autonome** : données
embarquées, aucune dépendance réseau, aucun traceur, aucune bibliothèque tierce.

Site : https://algolife-research.github.io/sante_publique_demos/

## Démos

| Démo | Sujet | Données |
|---|---|---|
| [`demos/meningocoque`](demos/meningocoque/) | Infections invasives à méningocoque et couverture vaccinale, 1995-2025 | déclaration obligatoire des IIM ; couvertures vaccinales départementales |

## Structure

```
index.html                     page d'accueil listant les démos (racine des GitHub Pages)
demos/<nom>/index.html         démo générée, autonome — ne pas éditer à la main
src/<nom>.template.html        gabarit source (HTML + CSS + JS), avec le jeton __DATA__
src/build_<nom>.py             script de construction : lit data/, injecte, écrit demos/
data/README.md                 provenance des données sources (les données ne sont pas versionnées)
data/odisse/*.csv              exports Odissé tels que téléchargés
data/geo/*.geojson             contours départementaux (france-geojson)
```

Le fichier servi est généré : on édite `src/<nom>.template.html`, puis on reconstruit.

## Reconstruire

Les données sources ne sont pas dans le dépôt (voir `data/README.md` pour leur
provenance et les commandes de téléchargement) : les récupérer dans `data/` avant de
reconstruire. Les démos publiées, elles, embarquent déjà leurs données.

```bash
pip install pandas
python src/build_meningocoque.py
```

Le script simplifie les contours (Douglas-Peucker), projette la métropole et place les
DOM en cartouches, agrège les cas et les populations par département, année et
sérogroupe, puis remplace `__DATA__` dans le gabarit.

## Ajouter une démo

1. `src/ma_demo.template.html` — gabarit avec `__DATA__` là où le JSON doit atterrir.
2. `src/build_ma_demo.py` — lecture des données, écriture de `demos/ma_demo/index.html`.
3. Une entrée `<a class="demo">` dans `index.html` et une ligne dans le tableau ci-dessus.

## Publication

GitHub Pages sert la branche `main` depuis la racine. Le fichier `.nojekyll` évite que
Jekyll n'ignore certains chemins.

## Licences

Code sous licence MIT (voir `LICENSE`). Données publiques sous Licence Ouverte / Open
Licence (Etalab), Santé publique France. Contours départementaux : projet
[france-geojson](https://github.com/gregoiredavid/france-geojson), Grégoire David.
Détail des jeux de données et de leurs sources dans `data/README.md`.
