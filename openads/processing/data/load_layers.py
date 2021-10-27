__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingOutputString,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProviderRegistry,
)

from openads.processing.data.base import BaseDataAlgorithm


class LoadLayersAlgorithm(BaseDataAlgorithm):
    """
    Chargement des couches openads depuis la base de données
    """

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"
    OUTPUT = "OUTPUT"
    OUTPUT_MSG = "OUTPUT MSG"

    def name(self):
        return "load_layers"

    def displayName(self):
        return "Chargement des couches depuis la base"

    def shortHelpString(self):
        return "Charger toutes les couches de la base de données."

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

        label = "Schéma"
        tooltip = "Nom du schéma des données openads"
        default = "openads"
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA,
            label,
            self.CONNECTION_NAME,
            defaultValue=default,
            optional=False,
        )
        param.setHelp(tooltip)
        self.addParameter(param)

        # OUTPUTS
        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, "Couches de sortie")
        )

        self.addOutput(QgsProcessingOutputString(self.OUTPUT_MSG, "Message de sortie"))

    def processAlgorithm(self, parameters, context, feedback):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema = self.parameterAsSchema(parameters, self.SCHEMA, context)
        feedback.pushInfo("## CONNEXION A LA BASE DE DONNEES ##")

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection(connection_name)
        result_msg, uri = self.get_uri(connection)
        feedback.pushInfo(result_msg)

        feedback.pushInfo("")
        feedback.pushInfo("## CHARGEMENT DES COUCHES ##")

        output_layers = []
        for name in self.layers_name:
            result_msg, layer = self.import_layer(context, uri, schema, name)
            feedback.pushInfo(result_msg)
            if layer:
                output_layers.append(layer.id())

        msg = "success"
        return {self.OUTPUT_MSG: msg, self.OUTPUT: output_layers}
