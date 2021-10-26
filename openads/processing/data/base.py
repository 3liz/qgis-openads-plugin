__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Union

from qgis.core import QgsDataSourceUri, QgsProcessingContext, QgsVectorLayer

from openads.processing.base import BaseProcessingAlgorithm


class BaseDataAlgorithm(BaseProcessingAlgorithm):
    def group(self):
        return "Import des données"

    def groupId(self):
        return "data"

    def init_layer(
        self,
        context: QgsProcessingContext,
        uri: QgsDataSourceUri,
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
