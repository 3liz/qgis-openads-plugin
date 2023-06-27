start_tests:
	@echo 'Start docker compose'
	@cd .docker && ./start.sh with-qgis

run_tests:
	@echo 'Running tests, containers must be running'
	@cd .docker && ./exec_tests.sh

stop_tests:
	@echo 'Stopping/killing containers'
	@cd .docker && ./stop.sh

tests: start_tests run_tests stop_tests

test_migration:
	@echo 'Testing migrations'
	@cd .docker && ./start.sh
	@cd .docker && ./install_migrate_generate.sh
	@cd .docker && ./stop.sh

schemaspy:
	@echo 'Generating schemaspy documentation'
	@cd .docker && ./start.sh
	rm -rf docs/database
	mkdir docs/database
	@cd .docker && ./install_db.sh
	@cd .docker && ./schemaspy.sh
	@cd .docker && ./stop.sh

processing-doc:
	@cd .docker && ./processing_doc.sh

reformat_sql:
	@echo 'Reformat SQL'
	@cd .docker && ./start.sh
	@cd .docker && ./install_db.sh
	@cd .docker && ./reformat_sql_install.sh
	@cd .docker && ./stop.sh

generate_sql:
	@echo 'Generate SQL into install files from service openads'
	cd openads/install/sql && ./export_database_structure_to_SQL.sh openads openads
