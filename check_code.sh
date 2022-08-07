#!/usr/bin/env bash
set -e +x
#set +x

echo "Running tests"
pytest

echo "Running check for style guide PEP8"
flake8 currencycom/

echo "DONE!"
#twine upload