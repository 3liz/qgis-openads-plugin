__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from pathlib import Path

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
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
    OVERRIDE = "OVERRIDE"
    DATABASE_VERSION = "DATABASE_VERSION"

    def name(self):
        return "create_database_structure"

    def displayName(self):
        return "Installation de la structure sur la base de données"

    def shortHelpString(self):
        return "Création de la structure de la base données. "

    def initAlgorithm(self, config):
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
            QgsProcessingParameterBoolean(
                self.OVERRIDE,
                (
                    "Écraser le schéma {} ? ** ATTENTION ** "
                    "Cela supprimera toutes les données !"
                ).format(SCHEMA),
                defaultValue=False,
                optional=False,
            )
        )

        self.addOutput(
            QgsProcessingOutputString(
                self.DATABASE_VERSION, "Version de la base de données"
            )
        )

    def checkParameterValues(self, parameters, context):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                "La connexion {} n'existe pas".format(connection_name)
            )

        if SCHEMA in connection.schemas():
            override = self.parameterAsBool(parameters, self.OVERRIDE, context)
            if not override:
                msg = (
                    "Le schéma {} existe déjà dans la base de données {} ! "
                    "Si vous voulez VRAIMENT supprimer et recréer le schéma "
                    "(et supprimer les données) cocher la case **Écraser**"
                ).format(SCHEMA, connection_name)
                return False, msg

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )

        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                "La connexion {} n'existe pas.".format(connection_name)
            )

        connection: QgsAbstractDatabaseProviderConnection

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override and SCHEMA in connection.schemas():
            feedback.pushInfo("Suppression du schéma {}…".format(SCHEMA))
            try:
                connection.dropSchema(SCHEMA, True)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))

        plugin_dir = plugin_path()
        plugin_version = pluginMetadata(PLUGIN_NAME, "version")
        dev_version = False
        run_migration = (
            os.getenv("TEST_DATABASE_INSTALL_{}".format(SCHEMA.upper())) is not None
        )
        if plugin_version in ("master", "dev") and not run_migration:
            feedback.reportError(
                "Be careful, running the install on a development branch!"
            )
            dev_version = True

        if run_migration:
            plugin_dir = plugin_test_data_path()
            feedback.reportError(
                "Be careful, running migrations on an empty database using {} "
                "instead of {}".format(run_migration, plugin_version)
            )
            plugin_version = run_migration

        self.create_sql_structure(connection, feedback, plugin_dir)

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
    ):
        """ Install all SQL files in the given connection. """
        sql_files = (
            "00_initialize_database.sql",
            "{}/10_FUNCTION.sql".format(SCHEMA),
            "{}/20_TABLE_SEQUENCE_DEFAULT.sql".format(SCHEMA),
            "{}/30_VIEW.sql".format(SCHEMA),
            "{}/40_INDEX.sql".format(SCHEMA),
            "{}/50_TRIGGER.sql".format(SCHEMA),
            "{}/60_CONSTRAINT.sql".format(SCHEMA),
            "{}/70_COMMENT.sql".format(SCHEMA),
            "99_finalize_database.sql",
        )
        for sf in sql_files:
            feedback.pushInfo(sf)
            sql_file = plugin_dir.joinpath("install/sql/{}".format(sf))
            with open(sql_file, "r") as f:
                sql = f.read()

            if len(sql.strip()) == 0:
                feedback.pushInfo("  Skipped (empty file)")
                continue

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
        plugin_version: int,
        run_migration: bool,
    ) -> int:
        """ Add the plugin version in the metadata table. """
        if run_migration or not dev_version:
            metadata_version = plugin_version
        else:
            migrations = available_migrations(000000)
            last_migration = migrations[-1]
            metadata_version = (
                last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
            )
            feedback.reportError("Latest migration is {}".format(metadata_version))
        sql = """
            INSERT INTO {}.qgis_plugin
            (id, version, version_date, status)
            VALUES (0, '{}', now()::timestamp(0), 1)""".format(
            SCHEMA, metadata_version
        )
        try:
            connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(str(e))
        feedback.pushInfo(
            "Version de la base de données '{}'.".format(metadata_version)
        )
        return metadata_version
