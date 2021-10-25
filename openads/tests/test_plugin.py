__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from unittest import main

from qgis.core import QgsVectorLayer

from openads.tests.base import TestCasePlugin


class TestPlugin(TestCasePlugin):
    def test_dialog(self):
        layer = QgsVectorLayer(
            "None?field=primary:integer&field=name:string(20)", "test", "memory"
        )
        self.assertTrue(layer.isValid())


if __name__ == "__main__":
    main()
