# Changelog

## Unreleased

## 0.10.0 - 2022-01-07

* Suppression de la colonne `dossier_importe_geosig` dans la table `dossiers_openads`.
* Relecture des logs lors de l'import des données contraintes.
* Ajout d'un paramètre code INSEE dans la couche des contraintes lors de l'import.
* Correction de l'import des parcelles si le schéma pour les données cadastre ne se nomme pas `cadastre`
* Amélioration de la documentation https://docs.3liz.org/qgis-openads-plugin

## 0.9.0 - 2021-12-10

* Ajout d'une variable dans le projet pour spécifier l'URL du projet
* Ajout d'un champ virtuel sur la couche `dossiers_openads` pour afficher l'URL du projet
* Ajout d'un trigger pour la gestion de la table `dossier_openads`
* Changement de la structure de la base de données
* Mise à jour de la documentation

## 0.1.0 - 2021-11-02

* Première version de l'extension
