__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsProcessingFeedback,
    QgsProviderConnectionException,
)

from openads.processing.base import BaseProcessingAlgorithm

SCHEMA = 'openads'


class BaseDatabaseAlgorithm(BaseProcessingAlgorithm):

    def group(self):
        return 'Base de données'

    def groupId(self):
        return 'database'

    @staticmethod
    def vacuum_all_tables(
            connection: QgsAbstractDatabaseProviderConnection, feedback: QgsProcessingFeedback):
        """ Execute a vacuum to recompute the feature count. """
        for table in connection.tables(SCHEMA):

            if table.tableName().startswith('v_'):
                # We can't vacuum a view
                continue

            sql = 'VACUUM ANALYSE {}.{};'.format(SCHEMA, table.tableName())
            feedback.pushDebugInfo(sql)
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                feedback.reportError(str(e))
