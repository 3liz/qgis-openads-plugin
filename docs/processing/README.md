---
hide:
  - navigation
---

# Processing

## Base de données


### Installation de la structure sur la base de données

Création de la structure de la base données.

![algo_id](./openads-create_database_structure.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Nom de la connexion dans QGIS pour se connecter à la base de données|✓|||
OVERRIDE|Écraser le schéma openads ? ** ATTENTION ** Cela supprimera toutes les données !|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
DATABASE_VERSION|Version de la base de données|String||


***


## Import des données


### Mise en place des données sur les communes

Ajout des données pour la table communes

![algo_id](./openads-data_commune.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Base de données de destination|✓|||
SCHEMA_CADASTRE|Schéma Cadastre|DatabaseSchema|Nom du schéma des données cadastre|✓||Default: cadastre <br> |
SCHEMA_OPENADS|Schéma openADS|DatabaseSchema|Nom du schéma des données openADS|✓||Default: openads <br> |
TRUNCATE_PARCELLES|Mise à jour de la table communes|Boolean||✓|||
IMPORT_PROJECT_LAYER|Importer la couche dans le projet|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
OUTPUT|Couches de sortie|MultipleLayers||
OUTPUT MSG|Message de sortie|String||


***


### Mise en place des données sur les parcelles

Ajout des données pour la table parcelles

![algo_id](./openads-data_parcelle.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
CONNECTION_NAME|Connexion PostgreSQL vers la base de données|ProviderConnection|Base de données de destination|✓|||
SCHEMA_CADASTRE|Schéma Cadastre|DatabaseSchema|Nom du schéma des données cadastre|✓||Default: cadastre <br> |
SCHEMA_OPENADS|Schéma openADS|DatabaseSchema|Nom du schéma des données openADS|✓||Default: openads <br> |
TRUNCATE_PARCELLES|Mise à jour de la table parcelles|Boolean||✓|||
IMPORT_PROJECT_LAYER|Importer la couche dans le projet|Boolean||✓|||


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
OUTPUT|Couches de sortie|MultipleLayers||
OUTPUT MSG|Message de sortie|String||


***
