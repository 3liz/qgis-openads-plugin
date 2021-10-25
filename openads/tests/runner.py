__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os
import unittest

from openads.tests.conftest import pytest_report_header


def _run_tests(test_suite, package_name, pattern):
    """Core function to test a test suite.

    :param test_suite: Unittest test suite
    """
    count = test_suite.countTestCases()
    print("######## Environment   ########")
    print(pytest_report_header(None))
    print(f"{count} tests has been discovered in {package_name} with pattern {pattern}")
    print("######## Running tests ########")
    results = unittest.TextTestRunner(verbosity=2).run(test_suite)
    print("######## Summary       ########")
    print(f"Errors               : {len(results.errors)}")
    print(f"Failures             : {len(results.failures)}")
    print(f"Expected failures    : {len(results.expectedFailures)}")
    print(f"Unexpected successes : {len(results.unexpectedSuccesses)}")
    print(f"Skip                 : {len(results.skipped)}")
    successes = results.testsRun - (
        len(results.errors)
        + len(results.failures)
        + len(results.expectedFailures)
        + len(results.unexpectedSuccesses)
        + len(results.skipped)
    )
    print(f"Successes            : {successes}")
    print(f"TOTAL                : {results.testsRun}")


def test_package(package=None, pattern="test_*.py"):
    """Test package.
    This function is called by CLI without arguments.

    :param package: The package to test.
    :type package: str

    :param pattern: The pattern of files to discover.
    :type pattern: str
    """
    pattern_environment = os.environ.get("TEST_PATTERN")
    if pattern_environment and pattern_environment != "default_pattern":
        print(f"Pattern from environment : {pattern_environment}")
        pattern = pattern_environment

    if package is None:
        package = os.path.dirname(os.path.realpath(__file__))

    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover(package, pattern=pattern)
    _run_tests(test_suite, package, pattern)


if __name__ == "__main__":
    test_package()
