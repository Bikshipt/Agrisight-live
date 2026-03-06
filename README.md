🌾 AgriSight Live

AgriSight Live is a real-time multimodal agricultural intelligence system that helps farmers detect crop diseases, predict their spread, analyze environmental risks, and make informed treatment and economic decisions.

The platform combines computer vision, predictive modeling, environmental analysis, and geospatial intelligence to transform a smartphone into a real-time agricultural decision support system.

📖 Overview

Crop diseases cause significant agricultural losses worldwide. In many regions, farmers identify problems only after visible damage appears, when crop yield has already been affected.

AgriSight Live addresses this problem by providing:

Real-time crop diagnosis using camera input

Disease progression prediction

Regional outbreak intelligence

Microclimate disease forecasting

Economic impact estimation

Satellite vegetation monitoring

Autonomous field scan analysis

Offline AI support for rural environments

Instead of acting as a simple plant disease detector, AgriSight Live functions as a predictive agricultural intelligence platform.

✨ Key Features

📸 Real-Time Crop Diagnosis

Farmers can point their smartphone camera at a crop leaf. The AI analyzes the live visual input and detects diseases, pests, or nutrient deficiencies. The system highlights affected areas using visual annotations and provides immediate explanations.

📈 Disease Progression Prediction

After detecting a disease, the system estimates how the infection may spread over time. Using disease growth models and environmental data, AgriSight Live forecasts infection probability and recommends intervention timing.

Example:

Disease detected: Rice Blast

Spread forecast: 3 days → 12% | 7 days → 41% | 10 days → 63%

Recommended action: Apply fungicide within 48 hours

💰 Economic Impact Estimation

AgriSight Live converts crop health issues into economic insights. Farmers receive estimates of potential yield loss, treatment cost, and expected financial savings from early intervention.

Example:

Expected yield loss: ₹10,200 per acre

Treatment cost: ₹1,200

Net savings if treated now: ₹9,000

🌍 Regional Outbreak Intelligence

Every crop scan contributes to a regional agricultural intelligence network. The system analyzes geospatial scan data to detect disease clusters and warn nearby farms about potential outbreaks.

Example:

Alert: Brown Planthopper outbreak detected

Distance: 12 km

Spread probability: 61%

🌦️ Microclimate Disease Forecasting

Crop diseases are strongly influenced by environmental conditions such as humidity, temperature, and rainfall. AgriSight Live integrates weather data to predict diseases before symptoms appear.

Example:

Risk Alert: Powdery Mildew

Probability: 68% within 4 days

Cause: High humidity conditions

Preventive action recommended

🛰️ Satellite Vegetation Monitoring

Satellite vegetation indices such as NDVI are used to detect crop stress and vegetation health trends across farms. This enables early detection of crop stress before visible symptoms appear in the field.

🚶 Autonomous Field Scan Mode

Farmers can record a short walk-through video of their field. The AI analyzes multiple frames, evaluates plant health across the field, and generates a summary report.

Example output:

Plants analyzed: 312

Healthy: 82%

Mild infection: 14%

Severe infection: 4%

📴 Offline AI Mode

Many rural areas have limited internet connectivity. AgriSight Live includes a lightweight on-device model that allows basic crop diagnosis without network access. Data synchronizes automatically once connectivity is restored.

🏗️ System Architecture

AgriSight Live is built as a distributed real-time AI platform.

📱 Mobile Web App (Camera + Voice)
        ↓ WebSocket Streaming
⚙️ Backend AI Orchestration Layer
        ↓ AI Reasoning Engines
☁️ Google Cloud Services


AI reasoning engines include:

Vision-based crop diagnosis

Disease progression simulation

Microclimate risk prediction

Yield impact estimation

Treatment optimization

Regional outbreak intelligence

Satellite vegetation analysis

Farm memory learning

🛠️ Technology Stack

Frontend: React, TypeScript, WebRTC, WebSockets

Backend: Python, FastAPI

AI and Data Processing: PyTorch, TensorFlow.js, OpenCV

Cloud Infrastructure: Google Cloud Run, Vertex AI, Firestore, Cloud Storage

Geospatial and Mapping: Mapbox GL JS

Infrastructure and Deployment: Docker, Terraform

🚀 Running the Project

Prerequisites

Python 3.10+

Node.js 18+

Docker

Google Cloud account

Clone Repository

git clone [https://github.com/yourusername/agrisight-live](https://github.com/yourusername/agrisight-live)
cd agrisight-live


Backend Setup

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload


Frontend Setup

cd frontend
npm install
npm run dev


Environment Variables

Create a .env file in the root directory:

GEMINI_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id
WEATHER_API_KEY=your_weather_api_key
MAPBOX_TOKEN=your_mapbox_token


☁️ Deployment

AgriSight Live is designed to run on Google Cloud.

Core services:

Cloud Run — backend API

Vertex AI — multimodal AI inference

Firestore — agricultural scan data

Cloud Storage — media storage

Infrastructure can be deployed using Terraform scripts located in the infra/ directory.

📁 Project Structure

agrisight-live/
│
├── frontend/
│   ├── components/
│   ├── services/
│   └── ui/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   └── data/
│
├── infra/
│   └── terraform/
│
├── docs/
│   └── architecture/
│
└── scripts/


🔮 Future Development

Future improvements include:

Expanded crop and disease datasets

Drone-based crop monitoring

IoT sensor integration for soil analysis

Improved predictive models for crop yield forecasting

Multi-farm agricultural intelligence networks

The long-term vision is to build a global crop intelligence platform that helps farmers detect, predict, and prevent agricultural losses.

📄 License

This project is licensed under the MIT License.
