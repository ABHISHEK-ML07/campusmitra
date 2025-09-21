# CampusMitra - Mental Wellness Platform
A hackathon project using Google Cloud tech (Vertex AI, Gemini, Firestore) for youth mental health.

## Features
- **MindChat**: Real-time AI chat with risk detection (Vertex AI).
- **HopeKit**: Generative therapeutic content (Gemini).
- **BookSafe**: Counselor booking with consent.
- **Counselor Meet**: Simulated session.
- **Dashboard**: Aggregated trends (Firestore).

## Setup
1. Install Anaconda: `conda create -n campusmitra python=3.12`
2. Activate: `conda activate campusmitra`
3. Install deps: `pip install -r requirements.txt`
4. Set env vars: `set GOOGLE_APPLICATION_CREDENTIALS=full\path\to\service_account.json` and `set GEMINI_API_KEY=your-key`.
5. Run: `python app.py`

## Demo
Access at http://localhost:5000 (backend) and open index.html (frontend).