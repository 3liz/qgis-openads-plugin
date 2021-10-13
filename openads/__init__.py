__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load the plugin main class.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    _ = iface
    # pylint: disable=import-outside-toplevel
    from openads.plugin import OpenAdsPlugin
    return OpenAdsPlugin()
