__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os
import time

from unittest import main

import processing

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProcessingFeedback,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
)

from openads.processing.provider import OpenAdsProvider as ProcessingProvider
from openads.qgis_plugin_tools import plugin_test_data_path
from openads.tests.base import TestCasePlugin


class MyFeedBack(QgsProcessingFeedback):
    def setProgressText(self, text: str):
        print(text)

    def pushInfo(self, info: str):
        print(info)

    def pushCommandInfo(self, info: str):
        print(info)

    def pushDebugInfo(self, info: str):
        print(info)

    def pushConsoleInfo(self, info: str):
        print(info)

    def reportError(self, error: str, fatalError: bool = False):
        print(error)


SCHEMA = "openads"


class TestImport(TestCasePlugin):
    def setUp(self) -> None:
        self.metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        self.connection = self.metadata.findConnection("test_database")
        self.connection: QgsAbstractDatabaseProviderConnection
        if SCHEMA in self.connection.schemas():
            self.connection.dropSchema(SCHEMA, True)
        # self.feedback = LoggerProcessingFeedBack()
        self.maxDiff = None

        provider = ProcessingProvider()
        registry = QgsApplication.processingRegistry()
        if not registry.providerById(provider.id()):
            registry.addProvider(provider)

        params = {
            "CONNECTION_NAME": "test_database",
            "OVERRIDE": True,
            "CRS": "EPSG:2154",
        }
        alg = "{}:create_database_structure".format(provider.id())
        processing.run(alg, params)

    def tearDown(self) -> None:
        if SCHEMA in self.connection.schemas():
            self.connection.dropSchema(SCHEMA, True)
        del self.connection
        time.sleep(1)

    def test_import_constraints(self):
        """Test to import constraints in the database."""
        params = {
            "ENTREE": str(
                plugin_test_data_path("PLUI", "248000747_INFO_SURF_20201109.shp")
            ),
            "CHAMP_ETIQUETTE": "LIBELLE",
            "CHAMP_TEXTE": "TXT",
            "VALEUR_GROUPE": "servitudes",
            "VALEUR_SOUS_GROUPE": "",
            "CONNECTION_NAME": os.getenv("TEST_QGIS_CONNEXION_NAME", "test_database"),
            "SCHEMA_OPENADS": "openads",
        }
        provider = ProcessingProvider()
        alg = "{}:data_constraints".format(provider.id())
        results = processing.run(alg, params)

        # We don't have municipalities
        self.assertEqual(results["COUNT_FEATURES"], 0)
        self.assertEqual(results["COUNT_NEW_CONSTRAINTS"], 5)

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection("test_database")

        source = QgsCoordinateReferenceSystem(4326)
        destination = QgsCoordinateReferenceSystem(2154)
        transform = QgsCoordinateTransform(source, destination, QgsProject.instance())

        communes = QgsVectorLayer(
            str(plugin_test_data_path("communes.geojson")), "communes", "ogr"
        )
        for feature in communes.getFeatures():
            geom = feature.geometry()
            geom.transform(transform)
            sql = (
                f"INSERT INTO openads.communes (nom, codeinsee, geom) "
                f"VALUES ("
                f"'{feature.attribute('name')}', "
                f"'{feature.attribute('insee')}', "
                f"ST_GeomFromText('{geom.asWkt()}', '2154')"
                f");"
            )
            # feedback.pushDebugInfo(sql)
            connection.executeSql(sql)

        results = processing.run(alg, params)

        # We have municipalities now
        self.assertEqual(results["COUNT_FEATURES"], 71)
        self.assertEqual(results["COUNT_NEW_CONSTRAINTS"], 0)


if __name__ == "__main__":
    main()
