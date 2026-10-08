#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

export AGENT_ENGINE_RESOURCE_NAME="projects/641596566969/locations/us-east1/reasoningEngines/5378438148638375936"
export AGENT_DIRECTORY="app"
export PORT="${PORT:-8081}"

exec .venv/bin/python main.py
