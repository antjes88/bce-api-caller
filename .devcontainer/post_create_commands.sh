#!/bin/bash
# shellcheck disable=SC1091,SC2059

sed -i 's/\r$//' /workspaces/exchange-rates-ingestion/cli/bin/exchange-rates-ingestion
chmod +x /workspaces/exchange-rates-ingestion/cli/bin/exchange-rates-ingestion
git config --global --add safe.directory /workspaces/exchange-rates-ingestion
gcloud auth application-default login

FILE="./.devcontainer/git_config.sh"
if [ -f "$FILE" ]; then
    chmod +x "$FILE"
    "$FILE"
else
    echo "$FILE not found. Follow instructions in README.md to set up git config. ### Configure Git"
fi