# ⚡ VESC Copilot

> **AI-Powered Hardware Advisor & Diagnostic Tuning Assistant for DIY Personal Electric Vehicles (PEVs)**

Built with **Google ADK (Agent Development Kit)**, **Vertex AI Agent Engine**, **Gemini**, and deployed via **FastAPI** to **Cloud Run**.

---

## 🛹 What is VESC Copilot?

**VESC Copilot** is a specialized autonomous assistant designed for builders and riders of DIY electric skateboards, Onewheel conversions, and custom PEVs running open-source VESC® motor controllers.

### Key Capabilities:
- **⚡ Hardware Compatibility & Specs**: Instant lookup of modern and popular VESC controllers (Fungineers Thor400, Thor301, Zeus400; Floatwheel GTV Kit, PintV Kit, ADV500; JetFleet F6, G18 GaN; ENNOID MK8/MK9 Pro), motor current limits, and battery voltage ceilings stored in **Firestore**.
- **🔍 Fault Diagnostics**: Step-by-step troubleshooting for critical VESC faults (e.g. `FAULT_CODE_DRV`, `ABS_OVER_CURRENT`, Hall sensor misconfigurations).
- **🌐 Real Community Grounding**: Cites real build logs and solutions from [pev.dev](https://pev.dev), creator videos (surfdado, Jay is Doing Stuff, Benjamin Vedder), and active Discord servers (*Float with VESC*, *VESC Development*, *Vescify*).
- **📐 Technical Wiring Schematics**: Dynamically generates high-voltage wiring diagrams and pinouts via Vertex AI Image Generation hosted on Cloud Storage.
- **🎨 Modern A2UI Experience**: Interactive frontend with dark mode, prompt chips, copy-to-clipboard cards, image lightbox modal, and clickable source links.

---

## 🎥 Video Demo

The repository includes a live recorded demonstration:
- [vesc_copilot_demo.mp4](./vesc_copilot_demo.mp4) — Full end-to-end demo featuring prompt chips, diagram generation, lightbox preview, and custom upbeat lo-fi soundtrack.

---

## 🏗️ Architecture

```
User (Browser) 
   │ 
   ▼ HTTP / JSON
FastAPI Proxy (`frontend/main.py`)
   │ 
   ▼ A2A Protocol (Agent-to-Agent)
Vertex AI Agent Engine (`app/agent.py`)
   ├── Gemini 2.5 Flash
   ├── Firestore DB (Hardware Catalog & Tune Presets)
   ├── Vertex AI Memory Bank (Long-term Rider Memory)
   ├── Cloud Storage (Generated Schematics & Diagrams)
   └── External Tooling (pev.dev, YouTube, Discord)
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- `agents-cli`: `uv tool install google-agents-cli`

### 2. Environment Setup
```bash
git clone https://github.com/conradopoole/buildwithgemini-vesc-copilot.git
cd buildwithgemini-vesc-copilot

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml

# Seed initial Firestore catalog
python seed_db.py
```

### 3. Run Development Playground
```bash
agents-cli playground
# Opens http://localhost:8000
```

### 4. Run Custom Web Chat UI
```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export AGENT_ENGINE_RESOURCE_NAME="projects/<project-num>/locations/us-east1/reasoningEngines/<id>"
export AGENT_DIRECTORY="app"
python main.py
# Opens http://localhost:8080
```

---

## 📖 Complete Handoff & Cloud Setup Guide

For step-by-step instructions on recreating the entire Google Cloud infrastructure, setting up IAM permissions, provisioning Memory Banks, and deploying both the backend agent and Cloud Run frontend, see **[HANDOFF.md](./HANDOFF.md)**.
