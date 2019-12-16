#!/usr/bin/env bash

set -ex

# Perform a release.
# See the release process documentation for details.
cd "$(mktemp -d)"
git clone git@github.com:"${GITHUB_OWNER}"/vws-cli.git
cd vws-cli
virtualenv -p python3 release
source release/bin/activate
pip install --editable .[dev]
python admin/release.py
