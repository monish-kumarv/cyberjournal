# CyberJournal

Cybersecurity professionals struggle with the cognitive load of tracking fragmented threat and news sources. CyberJournal (CJ) eliminates this fatigue by bringing everything into an AI-integrated platform-acting as a single source of truth for real-time security updates.

## Features
* **AI Threat Intelligence Analyst:** Query live feed data using Google's Gemini API to summarize critical updates, identify threat actors, and analyze affected systems.
* **High-Availability AI Architecture:** Implements a multi-model fallback waterfall (`gemini-3.8-flash` to `gemini-3.5-flash`) on the stable `v1` endpoint to maintain uptime during rate limits or model deprecations.
* **Live Feed Parsing:** Aggregates and structures live cybersecurity RSS feeds for real-time situational awareness.
* **Zero-Trust Secrets Management:** Utilizes Streamlit Community Cloud's native environment variables to keep API keys completely isolated from version control.

## Tech Stack
* **Frontend/Backend:** Python, Streamlit
* **AI Integration:** `google-genai` (v1 API)
* **Data Ingestion:** `feedparser`, `requests`
* **Deployment:** Streamlit Community Cloud (via GitHub CI/CD)

## Quick Start (Local Development)

**1. Clone the repository**
```bash
git clone [https://github.com/monish-kumarv/cyberjournal.git](https://github.com/monish-kumarv/cyberjournal.git)
cd cyberjournal
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure your API key**
Create a hidden Streamlit configuration folder and file:
```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```
Add your Gemini API key to `secrets.toml`:
```toml
GEMINI_API_KEY = "Your-Gemini-API-Key-Here"
```

**4. Run the application**
```bash
streamlit run app.py
```

## Security Note
This repository strictly isolates credentials. The `.gitignore` file prevents the `.streamlit/secrets.toml` file from being committed. If deploying to a cloud environment like Streamlit Community Cloud, inject the `GEMINI_API_KEY` directly via the platform's advanced secrets management console.
