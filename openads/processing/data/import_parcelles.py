__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from qgis.core import (
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


class ImportParcellesAlg(BaseDataAlgorithm):
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
        return "data_parcelle"

    def displayName(self):
        return "Import des parcelles"

    def shortHelpString(self):
        return "Ajout des données pour la table parcelles"

    def initAlgorithm(self, config):
        # INPUTS
        # Database connection parameters
        label = "Connexion PostgreSQL vers la base de données"
        tooltip = "Base de données de destination"
        default = QgsExpressionContextUtils.globalScope().variable(
            "openads_connection_name"
        )
        # noinspection PyArgumentList
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
        # noinspection PyArgumentList
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
        # noinspection PyArgumentList
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
                self.TRUNCATE_PARCELLES, "Mise à jour de la table parcelles"
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

            feedback.pushInfo("## Mise à jour des données parcelles ##")

            sql = f"""
                INSERT INTO {schema_openads}.parcelles (ccocom,ccodep,ccodir,ccopre,
                    ccosec,dnupla,geom,ident,ndeb,sdeb,nom,type)
                    SELECT p.ccocom, p.ccodep, p.ccodir, p.ccopre, p.ccosec, p.dnupla, pi.geom,
                           p.parcelle AS ident, p.dnvoiri, p.dindic, v.libvoi, v.natvoi
                    FROM {schema_cadastre}.parcelle p
                    JOIN {schema_cadastre}.parcelle_info pi on pi.geo_parcelle = p.parcelle
                    JOIN {schema_cadastre}.voie v on v.voie = pi.voie
                ON CONFLICT (ident) DO UPDATE SET
                    ccocom=EXCLUDED.ccocom, ccodep=EXCLUDED.ccodep,
                    ccodir=EXCLUDED.ccodir, ccopre=EXCLUDED.ccopre,
                    ccosec=EXCLUDED.ccosec, dnupla=EXCLUDED.dnupla,
                    geom=EXCLUDED.geom, ndeb=EXCLUDED.ndeb, sdeb=EXCLUDED.sdeb,
                    nom=EXCLUDED.nom, type=EXCLUDED.type;
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT_MSG: str(e), self.OUTPUT: []}

            feedback.pushInfo(
                f"# Suppression des parcelles dans {schema_openads}.parcelle qui n'existent plus #"
            )
            sql = f"""
                DELETE FROM {schema_openads}.parcelles
                WHERE ident NOT IN (
                    SELECT p.parcelle
                    FROM cadastre.parcelle p
                )
            """
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                connection.executeSql("ROLLBACK;")
                return {self.OUTPUT_MSG: str(e), self.OUTPUT: []}

        import_layer = self.parameterAsBool(
            parameters, self.IMPORT_PROJECT_LAYER, context
        )

        output_layers = []
        if import_layer:
            result_msg, uri = self.get_uri(connection)
            feedback.pushInfo(result_msg)

            feedback.pushInfo("")
            feedback.pushInfo("## CHARGEMENT DE LA COUCHE ##")

            name = "parcelles"
            result_msg, layer = self.import_layer(context, uri, schema_openads, name)
            feedback.pushInfo(result_msg)
            if layer:
                output_layers.append(layer.id())

        msg = "success"

        return {self.OUTPUT_MSG: msg, self.OUTPUT: output_layers}
