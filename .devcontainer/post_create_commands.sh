#!/bin/bash
# shellcheck disable=SC1091,SC2059

sed -i 's/\r$//' /workspaces/bce-api-caller/cli/bin/bce-api-caller
chmod +x /workspaces/bce-api-caller/cli/bin/bce-api-caller
git config --global --add safe.directory /workspaces/bce-api-caller
gcloud auth application-default login

FILE="./.devcontainer/git_config.sh"
if [ -f "$FILE" ]; then
    chmod +x "$FILE"
    "$FILE"
else
    echo "$FILE not found. Follow instructions in README.md to set up git config. ### Configure Git"
fi