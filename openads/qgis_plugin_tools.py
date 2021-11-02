"""Tools to work with resources files."""

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from pathlib import Path
from typing import List

from qgis.PyQt import uic


def plugin_path(*args) -> Path:
    """Return the path to the plugin root folder."""
    path = Path(__file__).resolve().parent
    for item in args:
        path = path.joinpath(item)

    return path


def resources_path(*args) -> Path:
    """Return the path to the plugin resources folder."""
    return plugin_path("resources", *args)


def plugin_test_data_path(*args) -> Path:
    """Return the path to the plugin test data folder."""
    return plugin_path("tests", "fixtures", *args)


def load_ui(*args):
    """Return the UI compiled file from the resources folder."""
    ui_class, _ = uic.loadUiType(resources_path("ui", *args))
    return ui_class


def available_migrations(minimum_version: int) -> List[str]:
    """Get all the upgrade SQL files since the provided version."""
    upgrade_dir = plugin_path("install", "sql", "upgrade")
    files = []

    for sql_file in upgrade_dir.iterdir():
        if not sql_file.is_file():
            continue

        if not sql_file.suffix == ".sql":
            continue

        current_version = format_version_integer(
            sql_file.name.replace("upgrade_to_", "").replace(".sql", "").strip()
        )

        if current_version > minimum_version:
            files.append([current_version, sql_file.name])

    def get_key(item):
        return item[0]

    sql_files = sorted(files, key=get_key)
    return [s[1] for s in sql_files]


def format_version_integer(version_string: str) -> int:
    """Transform version string to integers to allow comparing versions.

    Transform "0.1.2" into "000102"
    Transform "10.9.12" into "100912"
    """
    return int("".join([a.zfill(2) for a in version_string.strip().split(".")]))