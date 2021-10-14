__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from unittest import TestCase

from qgis.core import QgsApplication  # NOQA


class TestCasePlugin(TestCase):

    qgs = None

    @classmethod
    def setUpClass(cls):
        from qgis.utils import iface

        print(iface)
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()
        from qgis.utils import iface

        print(iface)

    @classmethod
    def tearDownClass(cls):
        cls.qgs.exitQgis()
