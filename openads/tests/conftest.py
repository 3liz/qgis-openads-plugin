"""Configuration file for PyTest."""

import sys

from typing import Dict

from osgeo import gdal
from qgis.core import Qgis
from qgis.PyQt import Qt

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


def pytest_report_header(config: Dict) -> str:
    """Used by PyTest and Unittest."""
    gdal_version = gdal.VersionInfo("VERSION_NUM")
    message = f"QGIS : {Qgis.releaseName()} {Qgis.versionInt()}\n"
    message += f"Python GDAL : {gdal_version}\n"
    message += f"Python : {sys.version}\n"
    # noinspection PyUnresolvedReferences
    message += f"QT : {Qt.QT_VERSION_STR}"
    return message
