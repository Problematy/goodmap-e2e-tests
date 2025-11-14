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

cleanup:
	pip remove goodmap
	npm remove
