__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Union

from qgis.core import (
    QgsDataSourceUri,
    QgsExpressionContextUtils,
    QgsProcessingContext,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingOutputString,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProviderRegistry,
    QgsVectorLayer,
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

    def init_layer(
        self,
        context: QgsProcessingContext,
        uri: str,
        schema: str,
        table: str,
        geom: str,
        sql: str,
        pk: str = None,
    ) -> Union[QgsVectorLayer, bool]:
        """Create vector layer from database table"""
        if pk:
            uri.setDataSource(schema, table, geom, sql, pk)
        else:
            uri.setDataSource(schema, table, geom, sql)
        layer = QgsVectorLayer(uri.uri(), table, "postgres")
        if not layer.isValid():
            return False
        context.temporaryLayerStore().addMapLayer(layer)
        context.addLayerToLoadOnCompletion(
            layer.id(),
            QgsProcessingContext.LayerDetails(table, context.project(), self.OUTPUT),
        )
        return layer

    def processAlgorithm(self, parameters, context, feedback):
        msg = ""
        output_layers = []
        layers_name = dict()
        layers_name["communes"] = dict()
        layers_name["communes"]["id"] = ""
        layers_name["communes"]["geom"] = "geom"
        layers_name["parcelles"] = dict()
        layers_name["parcelles"]["id"] = ""
        layers_name["parcelles"]["geom"] = "geom"
        layers_name["dossiers_openads"] = dict()
        layers_name["dossiers_openads"]["id"] = ""
        layers_name["dossiers_openads"]["geom"] = "geom"
        layers_name["contraintes"] = dict()
        layers_name["contraintes"]["id"] = ""
        layers_name["contraintes"]["geom"] = None

        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema = self.parameterAsSchema(parameters, self.SCHEMA, context)
        feedback.pushInfo("## CONNEXION A LA BASE DE DONNEES ##")

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection(connection_name)
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
                    context,
                    uri,
                    schema,
                    x,
                    layers_name[x]["geom"],
                    "",
                    layers_name[x]["id"],
                )
                if not result:
                    feedback.pushWarning(f"La couche {x} ne peut pas être chargée")
                else:
                    feedback.pushInfo(f"La couche {x} a été chargée")
                    output_layers.append(result.id())

        return {self.OUTPUT_MSG: msg, self.OUTPUT: output_layers}
