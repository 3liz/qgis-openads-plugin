__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from pathlib import Path
from typing import Dict

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsCoordinateReferenceSystem,
    QgsExpressionContextUtils,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterProviderConnection,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)
from qgis.utils import pluginMetadata

from openads.processing.database.base import BaseDatabaseAlgorithm
from openads.qgis_plugin_tools import (
    available_migrations,
    plugin_path,
    plugin_test_data_path,
)

PLUGIN_NAME = "openads"
SCHEMA = "openads"
DEFAULT_CONNECTION_NAME = "openads_connection_name"


class CreateDatabaseStructure(BaseDatabaseAlgorithm):
    """
    Creation of the database structure from scratch.
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    CRS = "CRS"
    OVERRIDE = "OVERRIDE"
    DATABASE_VERSION = "DATABASE_VERSION"

    def name(self):
        return "create_database_structure"

    def displayName(self):
        return "Installation de la base de données"

    def shortHelpString(self):
        return "Création de la structure de la base données. "

    @classmethod
    def default_crs(cls) -> str:
        """Default CRS for the database, without the authority."""
        return "2154"

    # noinspection PyMethodOverriding
    def initAlgorithm(self, config: Dict):
        connection_name = QgsExpressionContextUtils.globalScope().variable(
            DEFAULT_CONNECTION_NAME
        )
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            "Connexion PostgreSQL vers la base de données",
            "postgres",
            defaultValue=connection_name,
            optional=False,
        )
        param.setHelp(
            "Nom de la connexion dans QGIS pour se connecter à la base de données"
        )
        self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                "Projection",
                defaultValue=f"EPSG:{self.default_crs()}",
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERRIDE,
                (
                    f"Écraser le schéma {SCHEMA} ? ** ATTENTION ** "
                    "Cela supprimera toutes les données !"
                ),
                defaultValue=False,
                optional=False,
            )
        )

        self.addOutput(
            QgsProcessingOutputString(
                self.DATABASE_VERSION, "Version de la base de données"
            )
        )

    def checkParameterValues(self, parameters: Dict, context: QgsProcessingContext):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(f"La connexion {connection_name} n'existe pas")

        # noinspection PyUnresolvedReferences
        if SCHEMA in connection.schemas():
            override = self.parameterAsBool(parameters, self.OVERRIDE, context)
            if not override:
                msg = (
                    f"Le schéma {SCHEMA} existe déjà dans la base de données {connection_name} ! "
                    "Si vous voulez VRAIMENT supprimer et recréer le schéma "
                    "(et supprimer les données) cocher la case **Écraser**"
                )
                return False, msg

        crs = self.parameterAsCrs(parameters, self.CRS, context)
        if not crs.authid().startswith("EPSG:"):
            return False, "Le système de projection doit être de type EPSG."

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )

        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        connection: QgsAbstractDatabaseProviderConnection

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override and SCHEMA in connection.schemas():
            feedback.pushInfo(f"Suppression du schéma {SCHEMA}…")
            try:
                connection.dropSchema(SCHEMA, True)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))

        crs = self.parameterAsCrs(parameters, self.CRS, context)
        feedback.pushInfo(f"Projection de l'installation : {crs.authid()}")

        plugin_dir = plugin_path()
        plugin_version = pluginMetadata(PLUGIN_NAME, "version")
        dev_version = False
        run_migration = os.getenv(f"TEST_DATABASE_INSTALL_{SCHEMA.upper()}", False)
        if plugin_version in ("master", "dev") and not run_migration:
            feedback.reportError(
                "Be careful, running the install on a development branch!"
            )
            dev_version = True

        if run_migration:
            plugin_dir = plugin_test_data_path()
            feedback.reportError(
                "Be careful, running migrations on an empty database using "
                f"{run_migration} instead of {plugin_version}"
            )
            plugin_version = run_migration

        self.create_sql_structure(connection, feedback, plugin_dir, crs)

        metadata_version = self.add_version_info(
            connection, dev_version, feedback, plugin_version, run_migration
        )

        self.vacuum_all_tables(connection, feedback)

        if run_migration:
            feedback.reportError("You need to run migrations, old version installed !")

        results = {
            self.DATABASE_VERSION: metadata_version,
        }
        return results

    @staticmethod
    def create_sql_structure(
        connection: QgsAbstractDatabaseProviderConnection,
        feedback: QgsProcessingFeedback,
        plugin_dir: Path,
        crs: QgsCoordinateReferenceSystem,
    ):
        """Install all SQL files in the given connection."""
        sql_files = (
            "00_initialize_database.sql",
            f"{SCHEMA}/10_FUNCTION.sql",
            f"{SCHEMA}/20_TABLE_SEQUENCE_DEFAULT.sql",
            f"{SCHEMA}/30_VIEW.sql",
            f"{SCHEMA}/40_INDEX.sql",
            f"{SCHEMA}/50_TRIGGER.sql",
            f"{SCHEMA}/60_CONSTRAINT.sql",
            f"{SCHEMA}/70_COMMENT.sql",
            "99_finalize_database.sql",
        )
        for sf in sql_files:
            feedback.pushInfo(sf)
            sql_file = plugin_dir.joinpath(f"install/sql/{sf}")
            with open(sql_file, "r") as f:
                sql = f.read()

            if len(sql.strip()) == 0:
                feedback.pushInfo("  Skipped (empty file)")
                continue

            if crs.authid() != CreateDatabaseStructure.default_crs:
                sql = sql.replace(
                    CreateDatabaseStructure.default_crs(),
                    crs.authid().replace("EPSG:", ""),
                )

            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))
            feedback.pushInfo("  Success !")

    @staticmethod
    def add_version_info(
        connection: QgsAbstractDatabaseProviderConnection,
        dev_version: bool,
        feedback: QgsProcessingFeedback,
        plugin_version: str,
        run_migration: bool,
    ) -> int:
        """Add the plugin version in the metadata table."""
        if run_migration or not dev_version:
            metadata_version = plugin_version
        else:
            migrations = available_migrations(000000)
            last_migration = migrations[-1]
            metadata_version = (
                last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
            )
            feedback.reportError(f"Latest migration is {metadata_version}")
        sql = f"""
            INSERT INTO {SCHEMA}.qgis_plugin
            (id, version, version_date, status)
            VALUES (0, '{metadata_version}', now()::timestamp(0), 1)"""
        try:
            connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(str(e))
        feedback.pushInfo(f"Version de la base de données '{metadata_version}'.")
        return metadata_version
