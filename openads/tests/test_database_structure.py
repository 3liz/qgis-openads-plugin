"""Tests for database structure."""
import time

import processing

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsApplication,
    QgsProcessingException,
    QgsProviderRegistry,
)
from qgis.testing import unittest

from openads.processing.provider import OpenAdsProvider as ProcessingProvider
from openads.qgis_plugin_tools import available_migrations

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

VERSION = "0.0.1"
SCHEMA = "openads"
TABLES = (
    "communes",
    "dossiers_openads",
    "dossiers_sig",
    "geo_contraintes",
    "parcelles",
    "contraintes",
    "qgis_plugin",
)


class TestProcessing(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        self.connection = self.metadata.findConnection("test_database")
        self.connection: QgsAbstractDatabaseProviderConnection
        if SCHEMA in self.connection.schemas():
            self.connection.dropSchema(SCHEMA, True)
        # self.feedback = LoggerProcessingFeedBack()
        self.maxDiff = None

    def tearDown(self) -> None:
        del self.connection
        time.sleep(1)

    def test_install_database(self):
        """Test we can install the database."""
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
        results = processing.run(alg, params)

        # Take the last migration
        migrations = available_migrations(000000)
        last_migration = migrations[-1]
        metadata_version = (
            last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
        )

        self.assertEqual(metadata_version, results["DATABASE_VERSION"])

        tables = self.connection.tables(SCHEMA)
        tables = [t.tableName() for t in tables]
        self.assertCountEqual(TABLES, tables)

        params = {
            "CONNECTION_NAME": "test_database",
            "OVERRIDE": False,
        }
        with self.assertRaises(QgsProcessingException):
            processing.run(alg, params)
        # self.assertTrue(
        #     any("If you really want to remove and recreate the schema" in s for s in self.feedback.history))
