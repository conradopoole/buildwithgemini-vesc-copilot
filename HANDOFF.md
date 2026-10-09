# VESC Copilot - Complete Architecture & Local Setup Handoff Guide

> **Important**: This guide contains everything required to recreate, configure, run, and deploy **VESC Copilot** from scratch on your local machine using your personal Google Cloud account and the Antigravity IDE/CLI.

---

## 1. Executive Summary & Architecture Overview

**VESC Copilot** is a domain-expert autonomous AI assistant for DIY Personal Electric Vehicles (PEVs) such as VESC Onewheel conversions, e-skateboards, and e-bikes.

```
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                          │
│   (Custom Chat UI with Dark Mode, Prompt Chips, A2UI cards)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON (/chat)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Proxy (frontend/)                │
│    - Authenticates via ADC (Google Cloud Credentials)       │
│    - Maintains user session contexts                       │
│    - Communicates over Google A2A Protocol                  │
└──────────────────────────────┬──────────────────────────────┘
                               │ A2A Stream (RPC)
┌──────────────────────────────▼──────────────────────────────┐
│         Vertex AI Agent Engine (Reasoning Engine)           │
│                   google-adk / Gemini 2.5                   │
├─────────────────────────────────────────────────────────────┤
│  Tools & Integrations:                                      │
│  1. Firestore DB: Hardware catalog & tune presets           │
│  2. Vertex AI Memory Bank: Cross-session rider memory       │
│  3. Imagen / Gemini Image Gen: Technical wiring schematics  │
│  4. Cloud Storage: Public bucket for hosting schematics     │
│  5. pev.dev Forum Retrieval: Real DIY build logs & guides   │
│  6. YouTube Service: Video links from creator channels      │
│  7. Discord Service: Direct community invite links          │
│  8. A2UI Catalog v0.8: Formats rich cards with citations    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites for Your Local Machine

Ensure your laptop has the following tools installed:
- **Git**: `git --version`
- **Python 3.11+**: `python3 --version`
- **uv** (Fast Python package manager):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Google Cloud SDK (`gcloud`)**: [Install instructions](https://cloud.google.com/sdk/docs/install)
- **google-agents-cli**:
  ```bash
  uv tool install google-agents-cli
  ```
- **Antigravity CLI / Antigravity IDE**: (If using Google Antigravity).

---

## 3. Google Cloud Project Setup

On your personal Google Cloud account:

### Step 3.1: Create or Select a GCP Project
```bash
export PROJECT_ID="your-personal-gcp-project-id"
export REGION="us-east1"

gcloud config set project $PROJECT_ID
```

### Step 3.2: Enable Required APIs
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 3.3: Set Up Firestore
1. Go to **Google Cloud Console > Firestore**.
2. Create a database in **Native mode** (Default database: `(default)` in your region, e.g., `us-east1` or `nam5`).

### Step 3.4: Create a Public Cloud Storage Bucket for Diagrams
```bash
export BUCKET_NAME="vesc-diagrams-$PROJECT_ID"

# Create bucket
gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION

# Make bucket objects publicly readable for browser image rendering
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

### Step 3.5: Create a Vertex AI Memory Bank (Optional but Recommended)
In Vertex AI Agent Platform:
```bash
# Can be created via Python or Vertex AI Console for long-term memory
```

---

## 4. Local Workspace Initialization

### Step 4.1: Clone Your Repository
```bash
git clone https://github.com/conradopoole/buildwithgemini-vesc-copilot.git
cd buildwithgemini-vesc-copilot
```

### Step 4.2: Authenticate Locally
Authenticate your local shell with Google Cloud:
```bash
gcloud auth login
gcloud auth application-default login
```

### Step 4.3: Configure `.env`
Create a `.env` file in the root directory:
```bash
cat << EOF > .env
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=$REGION
GCS_IMAGE_BUCKET=$BUCKET_NAME
# If using Vertex AI Memory Bank:
# MEMORY_BANK_ID=projects/<your-project-number>/locations/us-east1/memoryBanks/<id>
