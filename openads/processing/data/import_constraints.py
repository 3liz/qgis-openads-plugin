__copyright__ = "Copyright 2022, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Callable, Dict, List, Tuple, Union

from qgis import processing
from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri,
    QgsExpression,
    QgsExpressionContextUtils,
    QgsFeatureRequest,
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeatureSource,
    QgsProcessingFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterString,
    QgsProcessingUtils,
    QgsProviderConnectionException,
    QgsProviderRegistry,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import NULL

from openads.processing.data.base import BaseDataAlgorithm


def sql_error_handler(func: Callable):
    """Decorator to catch sql exceptions."""

    def inner_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(f"Erreur SQL : {str(e)}")

    return inner_function


class ImportConstraintsAlg(BaseDataAlgorithm):
    """
    Import des données contraintes PLUI
    """

    INPUT = "ENTREE"
    INSEE_FIELD = "CHAMP_INSEE"
    LABEL_FIELD = "CHAMP_ETIQUETTE"
    TEXT_FIELD = "CHAMP_TEXTE"
    GROUP_VALUE = "VALEUR_GROUPE"
    SUB_GROUP_VALUE = "VALEUR_SOUS_GROUPE"
    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA_OPENADS = "SCHEMA_OPENADS"
    COUNT_FEATURES = "COUNT_FEATURES"
    COUNT_NEW_CONSTRAINTS = "COUNT_NEW_CONSTRAINTS"

    def name(self):
        return "data_constraints"

    def displayName(self):
        return "Import des contraintes"

    def shortHelpString(self):
        return "Ajout des données pour les tables des contraintes"

    # noinspection PyMethodOverriding
    def initAlgorithm(self, config: Dict):
        # noinspection PyUnresolvedReferences
        param = QgsProcessingParameterFeatureSource(
            self.INPUT,
            "Couche en entrée pour les contraintes",
            [QgsProcessing.TypeVectorPolygon],
        )
        param.setHelp("Couche vecteur qu'il faut importer dans la base de données")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.INSEE_FIELD,
            "Champ du code INSEE",
            parentLayerParameterName=self.INPUT,
            optional=True,
        )
        param.setHelp(
            "Champ du code INSEE pour la contrainte. Si le champ n'est pas fourni, le code INSEE proviendra "
            "de l'intersection avec la commune."
        )
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.LABEL_FIELD,
            "Champ des étiquettes",
            parentLayerParameterName=self.INPUT,
        )
        param.setHelp("Champ des étiquettes pour la contrainte")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterField(
            self.TEXT_FIELD,
            "Champ texte",
            parentLayerParameterName=self.INPUT,
        )
        param.setHelp("Champ texte pour la contrainte")
        self.addParameter(param)

        param = QgsProcessingParameterString(
            self.GROUP_VALUE,
            "Valeur pour le groupe",
        )
        param.setHelp(
            "Zonage, Contraintes, Servitudes, Droit de Préemption, Lotissement, ou tout autre valeur libre"
        )
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterString(
            self.SUB_GROUP_VALUE,
            "Valeur pour le sous-groupe",
            optional=True,
        )
        param.setHelp("Valeur libre")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            "Connexion PostgreSQL vers la base de données",
            "postgres",
            optional=False,
            defaultValue=QgsExpressionContextUtils.globalScope().variable(
                "openads_connection_name"
            ),
        )
        param.setHelp("Base de données de destination")
        self.addParameter(param)

        # noinspection PyArgumentList
        param = QgsProcessingParameterDatabaseSchema(
            self.SCHEMA_OPENADS,
            "Schéma openADS",
            self.CONNECTION_NAME,
            defaultValue="openads",
            optional=False,
        )
        param.setHelp("Nom du schéma des données openADS")
        self.addParameter(param)

        self.addOutput(
            QgsProcessingOutputNumber(self.COUNT_FEATURES, "Nombre d'entités importés")
        )

        self.addOutput(
            QgsProcessingOutputNumber(
                self.COUNT_NEW_CONSTRAINTS, "Nombre de nouvelles contraintes"
            )
        )

    # noinspection PyMethodOverriding
    def checkParameterValues(self, parameters: Dict, context: QgsProcessingContext):
        # noinspection PyArgumentList
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        # schema_openads = self.parameterAsSchema(
        #     parameters, self.SCHEMA_OPENADS, context
        # )
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )
        # TODO faire la vérification
        return super().checkParameterValues(parameters, context)

    # noinspection PyMethodOverriding
    def processAlgorithm(
        self,
        parameters: Dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        # noinspection PyArgumentList
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        schema_openads = self.parameterAsSchema(
            parameters, self.SCHEMA_OPENADS, context
        )

        # noinspection PyArgumentList
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        connection: QgsAbstractDatabaseProviderConnection
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        layer = self.parameterAsSource(parameters, self.INPUT, context)
        insee_field = self.parameterAsString(parameters, self.INSEE_FIELD, context)
        label_field = self.parameterAsString(parameters, self.LABEL_FIELD, context)
        text_field = self.parameterAsString(parameters, self.TEXT_FIELD, context)
        group = self.parameterAsString(parameters, self.GROUP_VALUE, context)
        sub_group = self.parameterAsString(parameters, self.SUB_GROUP_VALUE, context)

        if feedback.isCanceled():
            return {self.COUNT_FEATURES: 0, self.COUNT_NEW_CONSTRAINTS: 0}

        uniques = self.unique_couple_input(feedback, label_field, layer, text_field)

        connection.executeSql("BEGIN;")

        existing_constraints = self.existing_constraints_in_database(
            connection, schema_openads, group, sub_group, feedback
        )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return {self.COUNT_FEATURES: 0, self.COUNT_NEW_CONSTRAINTS: 0}

        missing_in_db = list(set(uniques) - set(existing_constraints.values()))

        feedback.pushInfo(
            f"Dans le jeu de données, il y a {len(missing_in_db)} nouvelles contrainte(s) : "
        )

        self.insert_new_constraints(
            connection,
            existing_constraints,
            feedback,
            group,
            missing_in_db,
            schema_openads,
            sub_group,
        )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return {self.COUNT_FEATURES: 0, self.COUNT_NEW_CONSTRAINTS: 0}

        crs = self.check_current_crs(connection, schema_openads, feedback)
        feedback.pushInfo(
            f"La projection du schéma {schema_openads} est en EPSG:{crs}."
        )

        layer = self.prepare_data(
            context,
            feedback,
            self.parameterAsLayer(parameters, self.INPUT, context),
            QgsCoordinateReferenceSystem(f"EPSG:{crs}"),
        )

        if not insee_field:
            feedback.pushInfo(
                "Le champ code INSEE n'est pas renseigné, l'import des contraintes va donc découper les "
                "contraintes selon les communes de la couche 'communes' dans le schéma 'openads'."
            )
            layer = self.split_layer_constraints(
                context, feedback, layer, connection, schema_openads
            )
            insee_field = "communes_codeinsee"
            insee_list = None
        else:
            feedback.pushInfo(
                f"Le code INSEE est '{insee_field}' dans la couche {layer.name()}. L'import va utiliser la "
                f"valeur de ce champ pour l'import."
            )
            sql = "SELECT codeinsee FROM openads.communes GROUP BY codeinsee;"
            result = connection.executeSql(sql)
            insee_list = [str(f[0]) for f in result]
            feedback.pushDebugInfo(
                f"Uniquement les contraintes dont le code INSEE est dans la liste suivante "
                f"{','.join(insee_list)} vont être importées car ils sont dans la table openads.communes."
            )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return {self.COUNT_FEATURES: 0, self.COUNT_NEW_CONSTRAINTS: 0}

        feedback.pushInfo("Insertion des geo-contraintes dans la base de données")
        success = self.import_new_geo_constraints(
            connection,
            feedback,
            insee_field,
            insee_list,
            label_field,
            layer,
            schema_openads,
            text_field,
            crs,
            group,
            sub_group,
        )

        if feedback.isCanceled():
            connection.executeSql("ROLLBACK;")
            return {self.COUNT_FEATURES: 0, self.COUNT_NEW_CONSTRAINTS: 0}

        connection.executeSql("COMMIT;")
        feedback.pushInfo(
            f"{success} nouvelles géo-contraintes dans la base de données"
        )
        return {
            self.COUNT_FEATURES: success,
            self.COUNT_NEW_CONSTRAINTS: len(missing_in_db),
        }

    @sql_error_handler
    def split_layer_constraints(
        self,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
        layer: QgsVectorLayer,
        connection: QgsAbstractDatabaseProviderConnection,
        schema: str,
    ) -> Union[QgsVectorLayer, None]:
        """Make the union between constraints and municipalities."""

        uri = QgsDataSourceUri(connection.uri())
        uri.setSchema(schema)
        uri.setTable("communes")
        uri.setKeyColumn("id_communes")
        uri.setGeometryColumn("geom")
        municipalities = QgsVectorLayer(uri.uri(), "communes", "postgres")

        feedback.pushInfo("Intersection des contraintes avec les communes")
        params = {
            "INPUT": layer,
            "OVERLAY": municipalities,
            "OVERLAY_FIELDS_PREFIX": "communes_",
            "OUTPUT": "memory:",
        }

        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:union",
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Transformation de multi vers unique de la nouvelle couche")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:multiparttosingleparts",
            {
                "INPUT": result["OUTPUT"],
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Intersection OK des contraintes avec les communes.")
        layer = QgsProcessingUtils.mapLayerFromString(result["OUTPUT"], context, True)
        return layer

    @sql_error_handler
    def import_new_geo_constraints(
        self,
        connection: QgsAbstractDatabaseProviderConnection,
        feedback: QgsProcessingFeedback,
        insee_field: str,
        insee_list: list,
        label_field: str,
        layer: QgsVectorLayer,
        schema: str,
        text_field: str,
        crs: str,
        group: str,
        sub_group: str,
    ) -> int:
        """Import in the database new geo-constraints."""
        success = 0
        fail = 0
        for feature in layer.getFeatures():
            content_label = self.clean_value(feature.attribute(label_field))
            content_text = self.clean_value(feature.attribute(text_field))
            insee_code = self.clean_value(feature.attribute(insee_field))

            if insee_code == "":
                feedback.pushDebugInfo(
                    f"Omission de l'entité {feature.id()} car elle n'a pas de code INSEE."
                )
                fail += 1
                continue

            if insee_list and str(insee_code) not in insee_list:
                feedback.pushDebugInfo(
                    f"Omission de l'entité {feature.id()} car son code INSEE n'est pas dans la table "
                    f"openads.communes"
                )
                fail += 1
                continue

            # noinspection PyArgumentList
            sql = (
                f"SELECT id_contraintes "
                f"FROM "
                f"{schema}.contraintes "
                f"WHERE "
                f"libelle = {QgsExpression.quotedString(content_label)} "
                f"AND texte = {QgsExpression.quotedString(content_text)} "
                f"AND groupe = {QgsExpression.quotedString(group)} "
                f"AND sous_groupe = {QgsExpression.quotedString(sub_group)};"
            )
            # feedback.pushDebugInfo(sql)
            result = connection.executeSql(sql)
            if len(result) == 0:
                # This case shouldn't happen ... it's covered before
                feedback.reportError(
                    f"Omission de l'entité {feature.id()} car elle n'y a pas de contrainte dans la base"
                )
                fail += 1
            else:
                # Useless, but better to check
                ids = [str(v[0]) for v in result]
                if len(ids) > 1:
                    feedback.reportError(
                        f"Erreur, il y a plusieurs identifiants lors de l'exécution : {sql}"
                    )
                    fail += 1
                    continue
                else:
                    ids = ids[0]

                # noinspection PyArgumentList
                sql = (
                    f"INSERT INTO {schema}.geo_contraintes (id_contraintes, texte, codeinsee, geom) "
                    f"VALUES ("
                    f"'{ids}', "
                    f"{QgsExpression.quotedString(content_text)}, "
                    f"'{insee_code}', "
                    f"ST_GeomFromText('{feature.geometry().asWkt()}', '{crs}')"
                    f") RETURNING id_geo_contraintes;"
                )
                # feedback.pushDebugInfo(sql)
                result = connection.executeSql(sql)
                feedback.pushDebugInfo(
                    f"    Insertion source ID {feature.id()} → ID {result[0][0]}"
                )
                success += 1

        if fail > 0:
            feedback.reportError(
                f"Veuillez lire logs ci-dessus, car il y a {fail} entités en défaut."
            )

        return success

    @classmethod
    def clean_value(cls, value: str) -> str:
        """Replace the NULL by empty string if needed."""
        if value == NULL:
            value = ""
        return value

    @classmethod
    @sql_error_handler
    def check_current_crs(
        cls,
        connection: QgsAbstractDatabaseProviderConnection,
        schema: str,
        feedback: QgsProcessingFeedback,
    ) -> str:
        """The current CRS in the database"""
        # Let's do it on communes
        # QGIS doesn't manage well if geometry_columns is not the search_path anyway
        sql = (
            f"SELECT srid FROM public.geometry_columns "
            f"WHERE f_table_schema = '{schema}' AND f_table_name = 'communes';"
        )
        feedback.pushInfo("Récupération du CRS de la base de données.")
        feedback.pushDebugInfo(sql)
        result = connection.executeSql(sql)
        return str(result[0][0])

    @staticmethod
    def existing_constraints_in_database(
        connection: QgsAbstractDatabaseProviderConnection,
        schema_openads: str,
        group: str,
        sub_group: str,
        feedback: QgsProcessingFeedback,
    ):
        """Return the list of existing constraints in database."""
        # annotation dict[str, Tuple[str, str]], Python 3.9
        uri = QgsDataSourceUri(connection.uri())
        uri.setSchema(schema_openads)
        uri.setTable("contraintes")
        uri.setKeyColumn("id_contraintes")
        existing_constraints = {}
        existing_constraints_layer = QgsVectorLayer(
            uri.uri(), "constraints", "postgres"
        )
        request = QgsFeatureRequest()
        request.setFilterExpression(
            f"\"groupe\" = '{group}' AND \"sous_groupe\" = '{sub_group}'"
        )
        for feature in existing_constraints_layer.getFeatures(request):
            existing_constraints[feature.attribute("id_contraintes")] = (
                feature.attribute("libelle"),
                feature.attribute("texte"),
            )
        feedback.pushInfo(
            f"Il y a {len(existing_constraints)} contrainte(s) dans la base de données concernant le groupe "
            f"'{group}' et le sous-groupe '{sub_group}'."
        )
        return existing_constraints

    @staticmethod
    @sql_error_handler
    def insert_new_constraints(
        connection: QgsAbstractDatabaseProviderConnection,
        existing_constraints: Dict,
        feedback: QgsProcessingFeedback,
        group: str,
        missing_in_db: List[Tuple[str, str]],
        schema_openads: str,
        sub_group: str,
    ):
        """Insert new constraints in the database and return the list of new IDs."""
        # annotation dict[str, Tuple[str, str]] Python 3.9
        for new in missing_in_db:
            # Quicker, to get the constraint_id with raw SQL query
            # noinspection PyArgumentList
            sql = (
                f"INSERT INTO {schema_openads}.contraintes (libelle, texte, groupe, sous_groupe) "
                f"VALUES ("
                f"{QgsExpression.quotedString(new[0])}, "
                f"{QgsExpression.quotedString(new[1])}, "
                f"{QgsExpression.quotedString(group)}, "
                f"{QgsExpression.quotedString(sub_group)}) "
                f"RETURNING id_contraintes;"
            )
            result = connection.executeSql(sql)
            feedback.pushDebugInfo(
                f"    Insertion dans la table 'contraintes' : {new} → ID {result[0][0]}"
            )
            existing_constraints[result[0][0]] = (new[0], new[1])
        return existing_constraints

    @staticmethod
    def prepare_data(
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
        layer: QgsVectorLayer,
        target_crs: QgsCoordinateReferenceSystem,
    ) -> Union[QgsVectorLayer, None]:
        """Preparing the data : fixing geometries, projection and multi."""
        feedback.pushInfo("Correction des géométries dans la couche en entrée")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:fixgeometries",
            {
                "INPUT": layer,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo("Transformation de multi vers unique")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:multiparttosingleparts",
            {
                "INPUT": result["OUTPUT"],
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        feedback.pushInfo(f"Reprojection vers {target_crs.authid()}")
        # noinspection PyUnresolvedReferences
        result = processing.run(
            "native:reprojectlayer",
            {
                "INPUT": result["OUTPUT"],
                "TARGET_CRS": target_crs,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return

        layer = QgsProcessingUtils.mapLayerFromString(result["OUTPUT"], context, True)
        feedback.pushInfo("Les données sont désormais OK pour l'import.")
        return layer

    @staticmethod
    def unique_couple_input(
        feedback: QgsProcessingFeedback,
        label_field: str,
        layer: QgsProcessingFeatureSource,
        text_field: str,
    ) -> List[Tuple[str, str]]:
        """Fetch unique couples in the input layer."""
        request = QgsFeatureRequest()
        request.setSubsetOfAttributes([label_field, text_field], layer.fields())
        uniques = []
        uniques_str = []
        for feature in layer.getFeatures(request):

            content_label = ImportConstraintsAlg.clean_value(
                feature.attribute(label_field)
            )
            content_text = ImportConstraintsAlg.clean_value(
                feature.attribute(text_field)
            )

            couple = (content_label, content_text)
            if couple not in uniques:
                uniques.append(couple)
                uniques_str.append(str(couple))

            if feedback.isCanceled():
                return []

        feedback.pushInfo(
            f"Dans la source, il y a {len(uniques)} couples uniques sur le couple "
            f"'{label_field}' : '{text_field}'"
        )
        feedback.pushDebugInfo(
            f"Liste des couples uniques dans la couche : {','.join(uniques_str)}"
        )

        return uniques
