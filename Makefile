GOODMAP_VERSION ?=
CONFIG_ ?= e2e_test_config.yml
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

run-e2e-stress-env:
	@PYTHONPATH="$(GOODMAP_PATH)" $$(cd "$(GOODMAP_PATH)" && poetry run which flask) --app "goodmap.goodmap:create_app(config_path='$(CONFIG_PATH)')" run

cleanup:
	pip remove goodmap
	npm remove
