__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from qgis.core import (
    QgsDataSourceUri,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from openads.processing.data.base import BaseDataAlgorithm


class ImportCommunesAlg(BaseDataAlgorithm):
    """
    Import des données Parcellaires depuis le cadastre
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA_OPENADS = "SCHEMA_OPENADS"
    SCHEMA_CADASTRE = "SCHEMA_CADASTRE"
    TRUNCATE_PARCELLES = "TRUNCATE_PARCELLES"
    IMPORT_PROJECT_LAYER = "IMPORT_PROJECT_LAYER"
    OUTPUT = "OUTPUT"
    OUTPUT_MSG = "OUTPUT MSG"

    def name(self):
        return "data_commune"

    def displayName(self):
        return "Mise en place des données sur les communes"

    def shortHelpString(self):
        return "Ajout des données pour la table communes"

    def initAlgorithm(self, config):
        # INPUTS
        # Database connection parameters
        label = "Connexion PostgreSQL vers la base de données"
        tooltip = "Base de données de destination"
        default = QgsExpressionContextUtils.globalScope().variable(
            "openads_connection_name"
        )
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            label,
            "postgres",
            optional=False,
            defaultValue=default,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        label = "Schéma Cadastre"
        tooltip = "Nom du schéma des données cadastre"
        default = "cadastre"
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_CADASTRE,
            label,
            self.CONNECTION_NAME,
            defaultValue=default,
            optional=False,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        label = "Schéma openADS"
        tooltip = "Nom du schéma des données openADS"
        default = "openads"
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_OPENADS,
            label,
            self.CONNECTION_NAME,
            defaultValue=default,
            optional=False,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.TRUNCATE_PARCELLES, "Mise à jour de la table communes"
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.IMPORT_PROJECT_LAYER, "Importer la couche dans le projet"
            )
        )

        # OUTPUTS
        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, "Couches de sortie")
        )

        self.addOutput(QgsProcessingOutputString(self.OUTPUT_MSG, "Message de sortie"))

    def processAlgorithm(self, parameters, context, feedback):

        # override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        output_layers = []
        layers_name = dict()
        layers_name["communes"] = "id_communes"
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema_cadastre = self.parameterAsSchema(
            parameters, self.SCHEMA_CADASTRE, context
        )
        schema_openads = self.parameterAsSchema(
            parameters, self.SCHEMA_OPENADS, context
        )

        data_update = self.parameterAsBool(parameters, self.TRUNCATE_PARCELLES, context)

        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )
        if data_update:
            feedback.pushInfo("# Vide la table openads.communes #")
            sql = """
                TRUNCATE openads.communes RESTART IDENTITY;
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT_MSG: str(e), self.OUTPUT: output_layers}

            feedback.pushInfo("## Mise à jour des données parcelles ##")

            sql = f"""
                INSERT INTO {schema_openads}.communes (anneemajic,ccodep,codcomm,nom,geom)
                SELECT cm.annee::int, cm.ccodep, cm.ccocom, cm.libcom, gc.geom
                FROM {schema_cadastre}.commune_majic cm
                JOIN {schema_cadastre}.geo_commune gc on gc.commune = cm.commune;
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT_MSG: str(e), self.OUTPUT: output_layers}

        import_layer = self.parameterAsBool(
            parameters, self.IMPORT_PROJECT_LAYER, context
        )

        if import_layer:
            uri = QgsDataSourceUri(connection.uri())
            is_host = uri.host() != ""
            if is_host:
                feedback.pushInfo("Connexion établie via l'hôte")
            else:
                feedback.pushInfo("Connexion établie via le service")
            feedback.pushInfo("")
            feedback.pushInfo("## CHARGEMENT DES COUCHES ##")
            for x in layers_name:
                if not context.project().mapLayersByName(x):
                    result = self.init_layer(
                        context, uri, schema_openads, x, "geom", "", layers_name[x]
                    )
                    if not result:
                        feedback.pushInfo(f"La couche {x} ne peut pas être chargée")
                    else:
                        feedback.pushInfo(f"La couche {x} a pu être chargée")
                        output_layers.append(result.id())

        msg = "success"

        return {self.OUTPUT_MSG: msg, self.OUTPUT: output_layers}
