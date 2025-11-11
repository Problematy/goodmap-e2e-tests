# E2E Testing Suite for Goodmap

This repository contains end-to-end testing infrastructure for the Goodmap application, automating validation of both frontend and backend components.

## Project Overview

This test suite verifies the functionality of the Goodmap application through Cypress-based end-to-end tests. It sets up a complete testing environment with:

- Backend (Flask-based Goodmap application)
- Frontend (Goodmap frontend application)
- Caddy as a reverse proxy to handle routing between components

## Prerequisites

- Node.js and npm
- Python 3.10+
- Poetry (Python dependency management)
- Caddy server

## Configuration

The test environment uses several configuration files:

- `e2e_test_config.yml`: Main configuration for the test instance
- `e2e_test_data.json`: Test data for the test suite
- `cypress.config.js`: Cypress testing framework configuration
- `Caddyfile`: Caddy server configuration for proxying requests

## Getting Started

### Installation

1. Install Goodmap dependencies:
    ```bash
    make install-goodmap
    ```

### Running Tests
Basic E2E Tests
1. Start the Goodmap backend:

    ```bash
    make run-e2e-goodmap
    ```

2. Start the frontend server (in a separate terminal):
    ```bash
    cd goodmap-frontend && make serve
    ```

3. Start Caddy (in a separate terminal):
    ```bash
    caddy run
    ```

4. Run the tests:
    ```bash
    make e2e-tests
    ```

5. Stress Tests
Generate stress test data:
    ```bash
    make e2e-stress-tests-generate-data
    ```

6. Start the stress test environment:
    ```bash
    make run-e2e-stress-env
    ```

7. Run stress tests:
    ```bash
    make e2e-stress-tests
    ```

### Continuous Integration

The repository includes GitHub Actions workflows to automatically run the tests:

- `.github/workflows/test.yml`: Triggered on pull requests and pushes to main
- `.github/workflows/test-base.yml`: Reusable workflow that can be called by other repositories
- `.github/workflows/test-comment.yml`: Posts test results as PR comments

## Using as a Reusable Workflow

Other repositories (e.g., `goodmap`, `goodmap-frontend`) can trigger E2E tests by calling the reusable workflow:

```yaml
name: Run E2E Tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  e2e-tests:
    uses: problematy/goodmap-e2e-tests/.github/workflows/test-base.yml@main
    permissions:
      contents: read
      pull-requests: write
    secrets: inherit
    with:
      # Version of goodmap to test (branch, tag, or SHA)
      goodmap-version: 'main'

      # Version of goodmap-frontend to test
      goodmap-frontend-version: 'main'

      # Version of e2e-tests to use
      goodmap-e2e-version: 'main'

      # Which repository is calling (goodmap, goodmap-frontend, or goodmap-e2e-tests)
      calling-repo: 'goodmap'

      # Optional: Custom paths (defaults work for most cases)
      # e2e-tests-path: 'goodmap-e2e-tests'
      # goodmap-path: 'goodmap'
      # goodmap-frontend-path: 'goodmap-frontend'

      # Optional: Custom config file
      # goodmap-config-path: 'e2e_test_config.yml'
```

### Workflow Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `goodmap-version` | Yes | - | Git ref (branch/tag/SHA) of goodmap to test |
| `goodmap-frontend-version` | Yes | - | Git ref of goodmap-frontend to test |
| `goodmap-e2e-version` | Yes | - | Git ref of e2e-tests to use |
| `calling-repo` | No | - | Repository calling the workflow (determines checkout behavior) |
| `e2e-tests-path` | No | `.` | Path where e2e-tests will be checked out |
| `goodmap-path` | No | `goodmap` | Path where goodmap will be checked out |
| `goodmap-frontend-path` | No | `goodmap-frontend` | Path where goodmap-frontend will be checked out |
| `goodmap-config-path` | No | `e2e_test_config.yml` | Config file for goodmap E2E tests |

**Note:** The `e2e-tests-path` parameter is critical for cross-repository usage. It ensures that composite actions and scripts are referenced from the correct repository location. When calling from another repository, this typically should be set to `goodmap-e2e-tests`.

### Example: Testing a goodmap PR

When a PR is created in the `goodmap` repository, automatically test it with the latest frontend:

```yaml
jobs:
  e2e-tests:
    uses: problematy/goodmap-e2e-tests/.github/workflows/test-base.yml@main
    permissions:
      contents: read
      pull-requests: write
    secrets: inherit
    with:
      goodmap-version: ${{ github.sha }}          # Test this PR
      goodmap-frontend-version: 'main'             # Latest frontend
      goodmap-e2e-version: 'main'                  # Latest tests
      calling-repo: 'goodmap'
      e2e-tests-path: 'goodmap-e2e-tests'          # Where e2e-tests will be checked out
      goodmap-path: '.'                            # Goodmap is already checked out here
```

## Reusable Components

### Path Handling for Cross-Repository Usage

When `test-base.yml` is called from another repository, it uses the `e2e-tests-path` input parameter to correctly reference scripts. The workflow calls bash scripts using dynamic paths like:

```bash
bash ${{ inputs.e2e-tests-path }}/.github/scripts/start-backend.sh
```

This ensures that resources are always loaded from the e2e-tests repository, regardless of which repository initiated the workflow.

### Bash Scripts

The repository provides reusable bash scripts for common tasks:

#### Start Backend Script
`.github/scripts/start-backend.sh`

Starts the Goodmap Flask backend with automatic health checking.

**Usage:**
```bash
start-backend.sh <config-path> <goodmap-path> <working-directory> <make-target> <log-file> <pid-file> [startup-wait-seconds]
```

**Parameters:**
- `config-path`: Path to Goodmap configuration file
- `goodmap-path`: Path to Goodmap repository
- `working-directory`: Working directory to run make from
- `make-target`: Make target to run (e.g., `run-e2e-env`)
- `log-file`: Path to store backend logs
- `pid-file`: Path to store backend PID
- `startup-wait-seconds`: Seconds to wait for startup (optional, default: 5)

**Example:**
```yaml
- name: Start backend
  run: |
    bash .github/scripts/start-backend.sh \
      "e2e_test_config.yml" \
      "${{ github.workspace }}/goodmap" \
      "goodmap" \
      "run-e2e-env" \
      "/tmp/backend.log" \
      "/tmp/backend.pid" \
      "5"
```

#### Stop Backend Script
`.github/scripts/stop-backend.sh`

Gracefully stops the Goodmap Flask backend.

**Usage:**
```bash
stop-backend.sh <pid-file> <config-pattern>
```

**Parameters:**
- `pid-file`: Path to the PID file
- `config-pattern`: Pattern to match flask process (e.g., `flask.*e2e_test_config`)

**Example:**
```yaml
- name: Stop backend
  if: always()
  run: |
    bash .github/scripts/stop-backend.sh \
      "/tmp/backend.pid" \
      "flask.*e2e_test_config"
```

### Performance Summary Script

`.github/scripts/generate-perf-summary.js`

Generates performance summaries from stress test results. Supports both GitHub Step Summaries and PR comment formats.

**Usage:**
```bash
node .github/scripts/generate-perf-summary.js <perf-json-path> [--format=github|pr-comment]
```

**Example:**
```yaml
- name: Add performance summary
  run: |
    node .github/scripts/generate-perf-summary.js \
      cypress/results/stress-test-perf.json \
      --format=github >> $GITHUB_STEP_SUMMARY
```


