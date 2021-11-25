__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import List

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterProviderConnection,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from openads.processing.database.base import BaseDatabaseAlgorithm
from openads.qgis_plugin_tools import (
    available_migrations,
    format_version_integer,
    plugin_path,
    version,
)

PLUGIN_NAME = "openads"
SCHEMA = "openads"
DEFAULT_CONNECTION_NAME = "openads_connection_name"


class UpgradeDatabaseStructure(BaseDatabaseAlgorithm):

    CONNECTION_NAME = "CONNECTION_NAME"
    CRS = "CRS"
    RUN_MIGRATIONS = "RUN_MIGRATIONS"
    OUTPUT_STATUS = "OUTPUT_STATUS"
    OUTPUT_STRING = "OUTPUT_STRING"

    def name(self):
        return "upgrade_database_structure"

    def displayName(self):
        return "Mise à jour de la base de données"

    def shortHelpString(self):
        return "Mise à jour de la structure de la base données. "

    @classmethod
    def default_crs(cls) -> str:
        """Default CRS for the database, without the authority."""
        return "2154"

    # noinspection PyMethodOverriding
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
            QgsProcessingParameterCrs(
                self.CRS,
                "Projection",
                defaultValue=f"EPSG:{self.default_crs()}",
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RUN_MIGRATIONS,
                "Cocher cette option pour lancer la mise-à-jour.",
                defaultValue=False,
                optional=False,
            )
        )
        # OUTPUTS
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_STATUS, "Output status"))
        self.addOutput(QgsProcessingOutputString(self.OUTPUT_STRING, "Output message"))

    def checkParameterValues(self, parameters, context):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection: QgsAbstractDatabaseProviderConnection = metadata.findConnection(
            connection_name
        )
        if not connection:
            raise QgsProcessingException(f"La connexion {connection_name} n'existe pas")

        run_migrations = self.parameterAsBool(parameters, self.RUN_MIGRATIONS, context)
        if not run_migrations:
            msg = "Vous devez cocher cette case pour réaliser la mise à jour !"
            return False, msg

        # Check database content
        if SCHEMA not in connection.schemas():
            override = self.parameterAsBool(parameters, self.RUN_MIGRATIONS, context)
            if not override:
                msg = "The schema {} does not exists in the database {} ! ".format(
                    SCHEMA, connection_name
                )
                return False, msg

        crs = self.parameterAsCrs(parameters, self.CRS, context)
        if not crs.authid().startswith("EPSG:"):
            return False, "Le système de projection doit être de type EPSG."

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection: QgsAbstractDatabaseProviderConnection = metadata.findConnection(
            connection_name
        )

        # Check run migration
        run_migrations = self.parameterAsBool(parameters, self.RUN_MIGRATIONS, context)
        if not run_migrations:
            msg = "Vous devez cocher cette case pour réaliser la mise à jour !"
            raise QgsProcessingException(msg)

        # Get database version
        sql = f"""
            SELECT version
            FROM {SCHEMA}.qgis_plugin
            WHERE status = 1
            ORDER BY version_date DESC, version DESC
            LIMIT 1;
        """
        try:
            data = connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(str(e))

        db_version = None
        for row in data:
            db_version = row[0]
        if not db_version:
            error_message = "Aucune version trouvée dans la base de données !"
            raise QgsProcessingException(error_message)

        feedback.pushInfo(f"Version de la base de données = {db_version}")

        # Get plugin version
        plugin_version = version()
        if plugin_version in ["master", "dev"]:
            migrations = available_migrations(000000)
            last_migration = migrations[-1]
            plugin_version = (
                last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
            )
            feedback.reportError(
                "Be careful, running the migrations on a development branch!"
            )
            feedback.reportError(f"Latest available migration is {plugin_version}")
        else:
            feedback.pushInfo(f"Version du plugin = {plugin_version}")

        # Return if nothing to do
        if db_version == plugin_version:
            return {
                self.OUTPUT_STATUS: 1,
                self.OUTPUT_STRING: (
                    " La version de la base de données et du plugin sont les mêmes. "
                    "Aucune mise-à-jour n'est nécessaire"
                ),
            }

        db_version_integer = format_version_integer(db_version)
        sql_files = available_migrations(db_version_integer)

        self.exec_sql(feedback, connection, sql_files)

        # Everything is fine, we now update to the plugin version
        self.upgrade_database_version(connection, plugin_version)

        msg = "*** LA STRUCTURE A BIEN ÉTÉ MISE À JOUR SUR LA BASE DE DONNÉES ***"
        feedback.pushInfo(msg)

        return {self.OUTPUT_STATUS: 1, self.OUTPUT_STRING: msg}

    def exec_sql(
        self,
        feedback: QgsProcessingFeedback,
        connection: QgsAbstractDatabaseProviderConnection,
        sql_files: List,
    ):
        """Run all migrations on the given connection."""
        # Loop sql files and run SQL code
        for sf in sql_files:
            sql_file = plugin_path().joinpath(f"install/sql/upgrade/{sf}")
            with open(sql_file, "r") as f:
                sql = f.read()

            if len(sql.strip()) == 0:
                feedback.pushInfo(f"* {sf} -- NON TRAITÉ (FICHIER VIDE)")
                continue

            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))

            # Add SQL database version in qgis_plugin table
            new_db_version = sf.replace("upgrade_to_", "").replace(".sql", "").strip()
            self.upgrade_database_version(connection, new_db_version)

            feedback.pushInfo(f"* {sf} -- OK !")

    @staticmethod
    def upgrade_database_version(
        connection: QgsAbstractDatabaseProviderConnection, plugin_version: str
    ):
        """Upgrade the database version in the given connection to the plugin version."""
        sql = f"""
            UPDATE {SCHEMA}.qgis_plugin
            SET (version, version_date) = ( '{plugin_version}', now()::timestamp(0));
        """
        try:
            connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(str(e))
