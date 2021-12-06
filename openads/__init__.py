__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.gui import QgisInterface


# noinspection PyPep8Naming
def classFactory(iface: QgisInterface):  # pylint: disable=invalid-name
    """Load the plugin main class.

    :param iface: A QGIS interface instance.
    """
    _ = iface
    # pylint: disable=import-outside-toplevel
    from openads.plugin import OpenAdsPlugin

    return OpenAdsPlugin()
