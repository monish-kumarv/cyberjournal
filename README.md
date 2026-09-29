# CyberJournal 🛡️

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-4285F4.svg)
![Security](https://img.shields.io/badge/Security-Zero_Trust-success.svg)

## 🔍 Problem Statement
A primary bottleneck in modern SecOps is threat feed fragmentation. Cybersecurity professionals struggle with the cognitive load of tracking fragmented threat and news sources. CyberJournal (CJ) eliminates this fatigue by bringing everything into an AI-integrated platform—acting as a single source of truth for real-time security updates.

## 📈 Business Impact
* **Time Saved:** Eliminates the manual hours spent context-switching between fragmented RSS feeds, distributed alerts, and vendor bulletins.
* **Quality Gained:** Reduces cognitive load and alert fatigue by using AI to instantly summarize critical updates, identify active threat actors, and extract CVEs directly from real-time data.
* **Path to Real Use:** Built as a scalable, serverless application that can be seamlessly integrated into existing enterprise SecOps workflows, incident response protocols, or daily threat hunting routines.

## 🚀 Working Prototype & Tech Stack
**Status:** Fully operational end-to-end prototype deployed via Streamlit Community Cloud (validated via live demonstration).

CyberJournal is deployed end-to-end as a fully functional, interactive web application with a CI/CD pipeline directly linked to this repository.
* **Frontend/Backend:** Python, Streamlit Community Cloud
* **AI Engine:** Google Gemini (`google-genai` v1 API)
* **High Availability AI Architecture:** Implements a fault-tolerant multi-model fallback loop (`gemini-3.8-flash` falling back to `gemini-3.5-flash`) to guarantee 100% prototype uptime and uninterrupted analysis during traffic spikes, endpoint deprecations, or API rate limits.
* **Data Ingestion:** `feedparser`, `requests` (Real-time aggregation without stale database dependencies)

## 🔒 Security Architecture
The application is engineered with strict enterprise-grade security parameters:
* **Zero-Trust Secrets Management:** The local `.streamlit/secrets.toml` configuration file is strictly isolated from version control via `.gitignore`. There are absolutely zero hardcoded credentials, API keys, or sensitive tokens exposed in this codebase.
* **Access & Deployment:** Production API keys are injected securely at runtime strictly through Streamlit Community Cloud's encrypted environment variables.
* **Data Handling:** RSS feeds and user queries are parsed and interrogated in real-time memory, eliminating the attack surface associated with vulnerable intermediary databases or long-term data storage.

---

### Local Execution (For Code & Architecture Review)

**1. Clone the repository**
```bash
git clone https://github.com/monish-kumarv/cyberjournal.git
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
