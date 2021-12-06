__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from unittest import TestCase

from qgis.core import QgsApplication  # NOQA


class TestCasePlugin(TestCase):

    qgs = None

    @classmethod
    def setUpClass(cls) -> None:
        from qgis.utils import iface

        if not iface:
            print("Init QGIS application")
            cls.qgs = QgsApplication([], False)
            cls.qgs.initQgis()
        else:
            cls.qgs = None

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.qgs:
            cls.qgs.exitQgis()
