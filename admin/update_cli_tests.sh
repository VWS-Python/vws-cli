#!/usr/bin/env bash

# There are CLI tests which check that --help output for various commands is
# as expected.
#
# Expected output is stored in files.
# This script updates those files.
#
# The expected use of this script:
#  * Make a change which changes expected help text for CLI commands
#  * Run this script
#  * Inspect the diff to check that changes are as expected
#  * Commit and push

set -euxo pipefail

export FIX_CLI_TESTS=1

mkdir -p tests/help_outputs
git rm -f tests/help_outputs/*.txt || true
pytest tests/test_help.py || true
git add tests/help_outputs/*.txt
