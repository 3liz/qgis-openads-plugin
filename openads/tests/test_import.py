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
    QgsExpression,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProject,
    QgsProviderRegistry,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import NULL

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

    def test_trigger_import_dossier(self):
        """Test import trigger dossier."""
        for i in (1, 2, 9):
            self.connection.executeSql(
                f"INSERT INTO openads.parcelles (ident, geom) "
                f"VALUES ({i}, ST_Multi(ST_Buffer(ST_MakePoint({i},{i}), 10)));"
            )

        result = self.connection.executeSql(
            "SELECT COUNT(*) AS count, STRING_AGG(\"id_parcelles\"::text, ',') FROM openads.parcelles;"
        )[0]
        self.assertEqual(3, result[0])
        self.assertEqual("1,2,3", result[1])

        count = self.connection.executeSql(
            "SELECT COUNT(*) FROM openads.dossiers_openads;"
        )[0][0]
        self.assertEqual(0, count)

        # Insertion d'un dossier avec des parcelles existantes dans la base
        self.connection.executeSql(
            "INSERT INTO openads.dossiers_openads (codeinsee, numero, parcelles) "
            "VALUES ('25047', '2', array[2]);"
        )
        results = self.connection.executeSql("SELECT * FROM openads.dossiers_openads;")
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual(row[0], 1)  # id_dossiers_openads
        self.assertEqual(row[1], "25047")  # codeinsee
        self.assertEqual(row[2], "2")  # numéro
        self.assertEqual(row[3], "{2}")  # parcelles
        self.assertGreaterEqual(row[4], 1)  # x
        self.assertGreaterEqual(row[5], 1)  # y
        self.assertNotEqual(row[7], NULL)  # geom
        # self.connection.executeSql('TRUNCATE openads.dossiers_openads RESTART IDENTITY;')

        # MAJ du dossier avec une parcelle non existante
        self.connection.executeSql(
            "UPDATE openads.dossiers_openads SET parcelles = array[2, 9999] "
            "WHERE id_dossiers_openads = 1;"
        )
        results = self.connection.executeSql("SELECT * FROM openads.dossiers_openads;")
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual(row[0], 1)  # id_dossiers_openads
        self.assertEqual(row[1], "25047")  # codeinsee
        self.assertEqual(row[2], "2")  # numéro
        self.assertEqual(row[3], "{2,9999}")  # parcelles
        self.assertEqual(row[4], NULL)  # x
        self.assertEqual(row[5], NULL)  # y
        self.assertNotEqual(row[7], NULL)  # geom
        self.connection.executeSql(
            "TRUNCATE openads.dossiers_openads RESTART IDENTITY;"
        )

        # Insertion d'un dossier avec des parcelles non existantes dans la base
        self.connection.executeSql(
            "INSERT INTO openads.dossiers_openads (codeinsee, numero, parcelles) "
            "VALUES ('25047', '3', array[9999]);"
        )
        results = self.connection.executeSql("SELECT * FROM openads.dossiers_openads;")
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual(row[0], 1)  # id_dossiers_openads
        self.assertEqual(row[1], "25047")  # codeinsee
        self.assertEqual(row[2], "3")  # numéro
        self.assertEqual(row[3], "{9999}")  # parcelles
        self.assertEqual(row[4], NULL)  # x
        self.assertEqual(row[5], NULL)  # y
        self.assertEqual(row[7], NULL)  # geom

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

    def test_load_layers_algorithm(self):
        """Test load layers algorithm."""
        params = {
            "CONNECTION_NAME": os.getenv("TEST_QGIS_CONNEXION_NAME", "test_database"),
            "SCHEMA": "openads",
            "URL_ADS": "https://demo.com?param=foo#anchor",
        }
        provider = ProcessingProvider()
        alg = "{}:load_layers".format(provider.id())

        project = QgsProject()
        variables = project.customVariables()
        self.assertNotIn("openads_url_ads", list(variables.keys()))
        context = QgsProcessingContext()
        context.setProject(project)

        with self.assertRaises(QgsProcessingException):
            # URL is not correct
            processing.run(alg, params, context=context)

        params["URL_ADS"] = "https://demo.com"

        results = processing.run(alg, params, context=context)

        variables = project.customVariables()
        self.assertEqual(variables["openads_url_ads"], "https://demo.com")

        layers = [
            layer for layer in results["OUTPUT"] if layer.name() == "dossiers_openads"
        ]
        layer = layers[0]

        index = layer.fields().indexFromName("lien_openads")
        self.assertGreaterEqual(index, 0)
        expression = layer.expressionField(index)
        self.assertTrue(expression.startswith("@openads_url_ads"))
        self.assertFalse(QgsExpression(expression).hasParserError())


if __name__ == "__main__":
    main()
