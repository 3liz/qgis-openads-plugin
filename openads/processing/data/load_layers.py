__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Dict, Tuple

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsExpressionContextUtils,
    QgsField,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingOutputString,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterString,
    QgsProviderRegistry,
)
from qgis.PyQt.QtCore import QUrl, QUrlQuery, QVariant

from openads.processing.data.base import BaseDataAlgorithm


class LoadLayersAlgorithm(BaseDataAlgorithm):
    """
    Chargement des couches openads depuis la base de données
    """

    @classmethod
    def virtual_field(cls) -> str:
        """Expression for the virtual field."""
        return "@openads_url_ads || '/app/web_entry.php?obj=dossier_instruction&value= '|| \"numero\""

    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"
    URL_ADS = "URL_ADS"
    OUTPUT = "OUTPUT"
    OUTPUT_MSG = "OUTPUT MSG"

    def name(self):
        return "load_layers"

    def displayName(self):
        return "Chargement des couches depuis la base"

    def shortHelpString(self):
        return "Charger toutes les couches de la base de données."

    def initAlgorithm(self, config: Dict):
        # INPUTS
        # Database connection parameters
        default = QgsExpressionContextUtils.globalScope().variable(
            "openads_connection_name"
        )
        # noinspection PyArgumentList
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            "Connexion PostgreSQL vers la base de données",
            "postgres",
            optional=False,
            defaultValue=default,
        )
        param.setHelp("Base de données de destination")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA,
            "Schéma",
            self.CONNECTION_NAME,
            defaultValue="openads",
            optional=False,
        )
        param.setHelp("Nom du schéma des données openads")
        self.addParameter(param)

        param = QgsProcessingParameterString(
            self.URL_ADS,
            "URL du dossier OpenADS",
            optional=True,
        )
        param.setHelp("L'URL du dossier OpenADS")
        self.addParameter(param)

        # OUTPUTS
        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, "Couches de sortie")
        )

        self.addOutput(QgsProcessingOutputString(self.OUTPUT_MSG, "Message de sortie"))

    def checkParameterValues(
        self, parameters: Dict, context: QgsProcessingContext
    ) -> Tuple[bool, str]:
        input_url = self.parameterAsString(parameters, self.URL_ADS, context)
        if input_url:
            # noinspection PyArgumentList
            url = QUrl(input_url)
            url.setQuery(QUrlQuery())  # Remove params
            url.setFragment("")  # Remove fragments, anchor, it will add a trailing '#'
            url = url.toString().rstrip("#")

            if input_url != url:
                return (
                    False,
                    "L'URL ne doit pas contenir d'ancre '#' ou de paramètres '?'. Peut-être qu'il s'agit de "
                    f"{url} ?",
                )

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema = self.parameterAsSchema(parameters, self.SCHEMA, context)

        key = "openads_url_ads"
        url = self.parameterAsString(parameters, self.URL_ADS, context)
        if url:
            QgsExpressionContextUtils.setProjectVariable(context.project(), key, url)
            feedback.pushInfo(
                f"Ajout de l'URL {url} dans la variable du projet '{key}'."
            )
        else:
            # The input was empty so the variable must be in the project already
            variables = context.project().customVariables()
            url = variables.get(key)
            if not url:
                # The virtual field needs this variable on runtime.
                raise QgsProcessingException(
                    f"Votre projet ne contient pas la variable {key}, vous devez donc renseigner la valeur "
                    f"pour l'URL"
                )

        feedback.pushInfo("## CONNEXION A LA BASE DE DONNEES ##")

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
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

                if name == "dossiers_openads":
                    field = QgsField("lien_openads", QVariant.String)
                    field.setAlias("Fiche du dossier sur openADS")
                    layer.addExpressionField(self.virtual_field(), field)

        msg = "success"
        return {self.OUTPUT_MSG: msg, self.OUTPUT: output_layers}
