__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from openads.processing.base import BaseProcessingAlgorithm


class BaseDataAlgorithm(BaseProcessingAlgorithm):
    def group(self):
        return "Import des données"

    def groupId(self):
        return "data"

