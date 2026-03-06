# AgriSight Live

AgriSight Live is a real-time, AI-powered agricultural analysis tool. It uses WebRTC and WebSocket to stream video and audio to a backend that orchestrates Gemini Live sessions, providing structured feedback on plant diseases, confidence scores, and recommended actions.

## Overview

AgriSight Live combines:
- real-time multimodal crop diagnosis (camera + audio)
- disease progression prediction and microclimate risk forecasting
- satellite vegetation monitoring (NDVI)
- yield and economic impact estimation
- treatment optimization and farm memory intelligence
- offline rural AI mode and field video scan analysis
- regional outbreak heatmaps and an AI voice assistant.

The backend runs on FastAPI (Cloud Run–ready) with Firestore, Cloud Storage, and Vertex AI / Gemini
integrations. The frontend is a mobile-first React PWA built with Vite and TailwindCSS.

## Quickstart (Local, Mock Mode)

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+

### Local Development (Mock Mode)
1. Copy `.env.example` to `.env` and fill in the required values (or leave as is for mock mode).
2. Start the services:
   ```bash
   make dev-start
   ```
3. Open `http://localhost:5173` in your browser.

### Environment Variables
See `.env.example` for a full list of required environment variables. At minimum:
- `GEMINI_API_KEY`: Gemini API key (not needed in MOCK_GEMINI / DEMO_MODE).
- `GOOGLE_CLOUD_PROJECT`: GCP project id.
- `WEATHER_API_KEY`: (optional) weather API key.
- `MAPBOX_TOKEN`: Mapbox token for outbreak map.

### Commands
- `make dev-start`: Starts frontend and backend locally via docker-compose.
- `make test`: Runs tests for both frontend and backend.
- `make lint`: Runs linters for both frontend and backend.
- `make build`: Builds production assets.
- `make deploy-staging`: Deploys to staging environment.

## Deployment (Google Cloud)

Infrastructure as code lives under `infra/terraform/` and provisions:
- Cloud Run service for the FastAPI backend
- Firestore (native mode)
- Cloud Storage bucket for images
- Vertex AI endpoint placeholder
- Secret Manager entries for `GEMINI_API_KEY`, `WEATHER_API_KEY`, `MAPBOX_TOKEN`.

High-level steps:
1. Set `GOOGLE_CLOUD_PROJECT` and authenticate `gcloud`.
2. From `infra/terraform/`:
   ```bash
   terraform init
   terraform plan -var="project_id=YOUR_PROJECT" -var="region=YOUR_REGION"
   terraform apply -var="project_id=YOUR_PROJECT" -var="region=YOUR_REGION" -auto-approve
   ```
3. Build and push backend image:
   ```bash
   cd backend
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/agrisight-backend:latest .
   ```

GitHub Actions workflow (`.github/workflows/ci.yml`) runs lint, tests, Docker build, and deploys
to a staging Cloud Run service on pushes to `main` (when GCP secrets are configured).

## Demo Mode

For hackathon demos without external dependencies, enable:
```bash
export DEMO_MODE=true
export MOCK_GEMINI=true
export MOCK_WEATHER=true
export MOCK_SATELLITE=true
```

Then run:
```bash
make dev-start
python scripts/demo_runner.py
```

This will exercise the main diagnosis → prediction → outbreak → economics → treatment pipeline
using deterministic mock data suitable for recording a smooth demo.

