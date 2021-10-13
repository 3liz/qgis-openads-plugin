__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from openads.processing.database.create import CreateDatabaseStructure
from openads.qgis_plugin_tools import resources_path

# from openads.processing.database.upgrade import UpgradeDatabaseStructure


class OpenAdsProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(CreateDatabaseStructure())
        # self.addAlgorithm(UpgradeDatabaseStructure())

    def id(self):  # NOQA: A003
        return "openads"

    def icon(self):
        return QIcon(str(resources_path("icons", "icon.png")))

    def name(self):
        return "OpenADS"

    def longName(self):
        return self.name()
