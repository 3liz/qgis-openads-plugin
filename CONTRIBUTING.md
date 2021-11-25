# Guide de contribution

## Pre-commit

Ce projet utilise l'outil [pre-commit](https://pre-commit.com/).

De préférence dans Python venv :

```bash
pip install -r requirements/dev.txt
pre-commit install
```

## Tests

Soit avec Docker dans le MakeFile
ou alors avec un QGIS/Postgis local

```bash
export QGIS_CUSTOM_CONFIG_PATH="/home/etienne/.local/share/QGIS/QGIS3/profiles/default"
export TEST_QGIS_CONNEXION_NAME="qgistest"
export QGIS_PREFIX_PATH=/home/etienne/dev/app/qgis-master
export PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages/:/home/etienne/dev/app/qgis-master/share/qgis/python/plugins/
pytest
```

## Base de données

Sur une nouvelle base de données, si vous souhaitez installer la base de données avec les migrations :

```python
import os
os.environ['TEST_DATABASE_INSTALL_OPENADS'] = '0.1.0'  # Enable
del os.environ['TEST_DATABASE_INSTALL_OPENADS']  # Disable
```
