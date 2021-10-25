"""Base class algorithm."""

from abc import abstractmethod

from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtGui import QIcon

from openads.qgis_plugin_tools import resources_path

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class BaseProcessingAlgorithm(QgsProcessingAlgorithm):
    def createInstance(self):
        return type(self)()

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagHideFromModeler

    def icon(self) -> QIcon:
        icon = resources_path("icons", "icon.png")
        if icon.exists():
            return QIcon(str(icon))
        else:
            return super().icon()

    def parameters_help_string(self) -> str:
        """ Return a formatted help string for all parameters. """
        help_string = ""
        for param in self.parameterDefinitions():
            info = param.help()
            if info:
                help_string += f"{param.name()} : {info}\n\n"

        return help_string

    @abstractmethod
    def shortHelpString(self):
        pass
