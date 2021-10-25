#!/usr/bin/env bash
export $(grep -v '^#' .env | xargs)

docker exec -it qgis sh \
  -c "export TEST_PATTERN=${TEST_PATTERN} && cd /tests_directory/${PLUGIN_NAME} && qgis_testrunner.sh tests.runner.test_package"
