start_tests:
	@echo 'Start docker-compose'
	@cd .docker && ./start.sh with-qgis

run_tests:
	@echo 'Running tests, containers must be running'
	@cd .docker && ./exec_tests.sh

stop_tests:
	@echo 'Stopping/killing containers'
	@cd .docker && docker-compose -f docker-compose-qgis.yml kill
	@cd .docker && docker-compose -f docker-compose-qgis.yml rm -f

tests: start_tests run_tests stop_tests

schemaspy:
	@echo 'Need to write it'

test_migration:
	@echo 'Need to write it'

processing-doc:
	@echo 'Need to write it'

reformat_sql:
	@echo 'Need to write it'

generate_sql:
	@echo 'Generate SQL into install files from service openads'
	cd openads/install/sql && ./export_database_structure_to_SQL.sh openads openads
