GOODMAP_VERSION ?=
CONFIG_PATH ?= e2e_test_config.yml
GOODMAP_PATH ?= .

lint-fix:
	npm run lint-fix
	npm run prettier-fix

lint-check:
	npm run lint
	npm run prettier

install-test-dependencies:
	npm install

e2e-tests:
	node_modules/cypress/bin/cypress run --browser chromium --spec "cypress/e2e/basic-test/*.cy.js"

e2e-stress-tests-generate-data:
	python cypress/support/generate_stress_test_data.py

e2e-stress-tests:
	node_modules/cypress/bin/cypress run --browser chromium --spec cypress/e2e/stress-test/*

cleanup:
	pip remove goodmap
	npm remove

run-e2e-env:
	poetry --project '$(GOODMAP_PATH)' run flask --app "goodmap.goodmap:create_app(config_path='$(CONFIG_PATH)')" --debug run

