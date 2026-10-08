#!/bin/bash
# Launch ADK Web with Agent Engine Memory Bank
MEMORY_BANK_ID="1105648002170617856"
uv run adk web . --port 8080 --reload_agents --memory_service_uri="agentengine://${MEMORY_BANK_ID}"
