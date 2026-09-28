import html
import re
import time
from datetime import datetime, timezone
import feedparser
import requests
import streamlit as st
from google import genai

# --- Page Configuration ---
st.set_page_config(
    page_title="Cyber Journal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- High-End SecOps Dark Theme CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0B0F17 !important; font-family: -apple-system, sans-serif; }
    [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; overflow-x: auto !important;
        gap: 16px !important; padding-bottom: 24px !important;
    }
    [data-testid="column"], [data-testid="stColumn"] { 
        min-width: 300px !important; 
        max-width: 300px !important; 
        flex: 0 0 300px !important; 
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #111622; border: 1px solid #1E293B !important;
        border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    div[data-testid="stVerticalBlock"] > div[style*="overflow"] { padding-right: 6px !important; }
    .card-link-wrapper { text-decoration: none !important; color: inherit !important; display: block; }
    .threat-card {
        background: #161F30; border: 1px solid #223049; border-radius: 8px;
        padding: 16px; margin-bottom: 12px; transition: all 0.15s ease-in-out;
        display: flex; flex-direction: column;
    }
    .threat-card:hover { border-color: #38BDF8; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,240,255,0.08); cursor: pointer; }
    
    .card-meta { display: flex; align-items: center; justify-content: flex-end; margin-bottom: 10px; font-size: 11px; font-weight: 600; letter-spacing: 0.4px; }
    .card-time { color: #64748B; font-family: monospace; }
    .card-title {
        color: #F1F5F9 !important; font-size: 14.5px; font-weight: 600; line-height: 1.45;
        margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }
    .threat-card:hover .card-title { color: #38BDF8 !important; }
    .card-snippet { color: #94A3B8; font-size: 13px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    ::-webkit-scrollbar { width: 6px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0B0F17; }
    ::-webkit-scrollbar-thumb { background: #223049; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #38BDF8; }
    
    span[data-baseweb="tag"] {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
        border: 1px solid #0284C7 !important;
    }
    span[data-baseweb="tag"] span {
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Security: Strictly Enforce Secrets File ---
try:
    api_key_to_use = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("🚨 Configuration Error: Gemini API Key is missing. Please add it to your .streamlit/secrets.toml file locally, or to the App Secrets in Streamlit Cloud.")
    st.stop()

# --- Feed Catalog ---
FEEDS = {
    "Cyber News": {
        "BleepingComputer": {"url": "https://www.bleepingcomputer.com/feed/", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.12)"},
        "The Hacker News": {"url": "https://feeds.feedburner.com/TheHackersNews", "color": "#10B981", "bg": "rgba(16, 185, 129, 0.12)"},
        "Dark Reading": {"url": "https://www.darkreading.com/rss.xml", "color": "#06B6D4", "bg": "rgba(6, 182, 212, 0.12)"},
        "The Register": {"url": "https://www.theregister.com/security/headlines.atom", "color": "#DC2626", "bg": "rgba(220, 38, 38, 0.12)"},
        "SecurityWeek": {"url": "https://feeds.feedburner.com/securityweek", "color": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.12)"},
        "The Record": {"url": "https://therecord.media/feed/", "color": "#EAB308", "bg": "rgba(234, 179, 8, 0.12)"},
        "Help Net Security": {"url": "https://www.helpnetsecurity.com/feed/", "color": "#3B82F6", "bg": "rgba(59, 130, 246, 0.12)"},
        "CyberScoop": {"url": "https://www.cyberscoop.com/feed/", "color": "#EC4899", "bg": "rgba(236, 72, 153, 0.12)"},
        "InfoSecurity Mag": {"url": "https://www.infosecurity-magazine.com/rss/news/", "color": "#14B8A6", "bg": "rgba(20, 184, 166, 0.12)"},
        "Security Affairs": {"url": "https://securityaffairs.com/feed", "color": "#F43F5E", "bg": "rgba(244, 63, 94, 0.12)"},
        "Wired Security": {"url": "https://www.wired.com/feed/category/security/latest/rss", "color": "#000000", "bg": "rgba(156, 163, 175, 0.2)"},
        "TechCrunch Security": {"url": "https://techcrunch.com/category/security/feed/", "color": "#16A34A", "bg": "rgba(22, 163, 74, 0.12)"},
        "ZDNet Security": {"url": "https://www.zdnet.com/topic/security/rss.xml", "color": "#2563EB", "bg": "rgba(37, 99, 235, 0.12)"},
        "Schneier on Security": {"url": "https://www.schneier.com/feed/", "color": "#64748B", "bg": "rgba(100, 116, 139, 0.12)"},
        "Graham Cluley": {"url": "https://grahamcluley.com/feed/", "color": "#84CC16", "bg": "rgba(132, 204, 22, 0.12)"},
        "CSO Online": {"url": "https://www.csoonline.com/feed/", "color": "#7C3AED", "bg": "rgba(124, 58, 237, 0.12)"}
    },
    "Advisories": {
        "CISA KEV Catalog": {"url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", "color": "#EAB308", "bg": "rgba(234, 179, 8, 0.12)"},
        "CISA Cyber Alerts (US)": {"url": "https://www.cisa.gov/uscert/ncas/alerts.xml", "color": "#0284C7", "bg": "rgba(2, 132, 199, 0.12)"},
        "NCSC Advisories (UK)": {"url": "https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml", "color": "#1D4ED8", "bg": "rgba(29, 78, 216, 0.12)"},
        "CERT-EU (Europe)": {"url": "https://cert.europa.eu/publications/security-advisories-rss", "color": "#2563EB", "bg": "rgba(37, 99, 235, 0.12)"},
        "CCCS Alerts (Canada)": {"url": "https://cyber.gc.ca/api/cccs/atom/v1/get?feed=alerts_advisories&lang=en", "color": "#DC2626", "bg": "rgba(220, 38, 38, 0.12)"},
        "SANS Internet Storm Center": {"url": "https://isc.sans.edu/rssfeed.xml", "color": "#EA580C", "bg": "rgba(234, 88, 12, 0.12)"}
    },
    "Vendor Feeds": {
        "Palo Alto Unit 42": {"url": "https://unit42.paloaltonetworks.com/feed/", "color": "#F97316", "bg": "rgba(249, 115, 22, 0.12)"},
        "Microsoft Security": {"url": "https://www.microsoft.com/security/blog/feed/", "color": "#059669", "bg": "rgba(5, 150, 105, 0.12)"},
        "CrowdStrike": {"url": "https://www.crowdstrike.com/blog/feed/", "color": "#FC0000", "bg": "rgba(252, 0, 0, 0.12)"},
        "Cisco Talos": {"url": "https://blog.talosintelligence.com/rss/", "color": "#14B8A6", "bg": "rgba(20, 184, 166, 0.12)"},
        "Check Point Research": {"url": "https://research.checkpoint.com/feed/", "color": "#E91E63", "bg": "rgba(233, 30, 99, 0.12)"}
    }
}

# --- Session State Setup ---
if "cj_chat_history" not in st.session_state:
    st.session_state["cj_chat_history"] = []

# --- Intelligent Cleaners & Helpers ---
def format_relative_time(entry):
    pub_parsed = entry.get('published_parsed')
    if pub_parsed:
        try:
            entry_time = datetime.fromtimestamp(time.mktime(pub_parsed), tz=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - entry_time
            seconds = int(delta.total_seconds())

            if seconds < 3600: return f"{max(1, seconds // 60)}m ago"
            if seconds < 86400: return f"{seconds // 3600}h ago"
            if seconds < 604800: return f"{seconds // 86400}d ago"
            return entry_time.strftime("%b %d")
        except Exception:
            pass
    return "Recent"

@st.cache_data(ttl=600, show_spinner=False)
def fetch_feed(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # ATTEMPT 0: CISA KEV Native JSON Intercept
    if "known_exploited_vulnerabilities.json" in url:
        try:
            resp = requests.get(url, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                kev_data = resp.json()
                entries = []
                vulns = sorted(kev_data.get("vulnerabilities", []), key=lambda x: x.get("dateAdded", ""), reverse=True)
                for v in vulns[:50]:
                    pub_str = v.get("dateAdded", "")
                    pub_parsed = None
                    if pub_str:
                        try:
                            pub_parsed = time.strptime(pub_str, "%Y-%m-%d")
                        except ValueError:
                            pass
                    
                    entries.append({
                        "title": f"{v.get('cveID')} - {v.get('vulnerabilityName')}",
                        "link": f"https://nvd.nist.gov/vuln/detail/{v.get('cveID')}",
                        "summary": v.get("shortDescription", "No description provided."),
                        "published": pub_str,
                        "published_parsed": pub_parsed
                    })
                return entries
        except Exception:
            pass
        return []
    
    # ATTEMPT 1: Direct Connection
    try:
        response = requests.get(url, headers=headers, timeout=5.0)
        if response.status_code == 200:
            parsed = feedparser.parse(response.content)
            if parsed.entries:
                return parsed.entries
    except Exception:
        pass
        
    # ATTEMPT 2: JSON API Fallback
    try:
        rss2json_url = f"https://api.rss2json.com/v1/api.json?rss_url={url}"
        proxy_response = requests.get(rss2json_url, timeout=8.0)
        if proxy_response.status_code == 200:
            data = proxy_response.json()
            if data.get("status") == "ok":
                entries = []
                for item in data.get("items", []):
                    pub_str = item.get("pubDate", "")
                    pub_parsed = None
                    if pub_str:
                        try:
                            pub_parsed = time.strptime(pub_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass
                    entries.append({
                        "title": item.get("title", "Advisory Notice"),
                        "link": item.get("link", "#"),
                        "summary": item.get("description", ""),
                        "published": pub_str,
                        "published_parsed": pub_parsed
                    })
                return entries
    except Exception:
        pass
        
    return []

def clean_summary_text(raw_html, max_chars=180):
    if not raw_html: return ""
    text = html.unescape(raw_html)
    text = re.sub(r"<[^>]+>", "", text)
    clean = " ".join(text.split())
    if len(clean) > max_chars:
        return clean[:max_chars].rsplit(" ", 1)[0] + "..."
    return clean

# --- Gemini AI Engines ---
def ask_cj_analyst(query, context_corpus, api_key):
    if not api_key:
        return "Please configure a Gemini API key to interact with CJ."
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are 'CJ' (Cyber Journal AI), an authoritative Senior Cyber Threat Intelligence analyst.
Answer the user's question directly, clearly, and concisely using the real-time threat feed context provided below.
If specific CVEs, threat actors, zero-days, or affected systems are mentioned in the context, cite them directly.

Feed Context:
{context_corpus}

User Inquiry: {query}
"""
        
        # High Availability Waterfall: Exhaustive list of current, lightweight, and legacy models
        available_models = [
            "gemini-3.8-flash", 
            "gemini-3.8-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ]
        last_error = ""
        
        for model_name in available_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                last_error = str(e)
                continue
                
        return f"CJ Analyst error: All fallback models are temporarily overloaded. Last error: {last_error}"
        
    except Exception as e:
        return f"CJ Analyst error: Failed to initialize client. {str(e)}"

# --- Sidebar Controls ---
st.sidebar.markdown("### 🛡️ Radar Control")
selected_cat = st.sidebar.selectbox("Category", list(FEEDS.keys()))

st.sidebar.divider()
st.sidebar.markdown("#### 🎛️ Active Streams")
st.sidebar.caption("The order you select these determines their left-to-right layout.")

available_providers = list(FEEDS[selected_cat].keys())
active_providers = st.sidebar.multiselect(
    "Visible Columns", 
    options=available_providers, 
    default=available_providers[:4]
)

st.sidebar.divider()
if st.sidebar.button("🔄 Force Sync Feeds", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- Collect and Index Visible Content ---
deck_data = {}
raw_context_lines = []

with st.spinner("Connecting to live intelligence feeds..."):
    for provider_name in active_providers:
        provider_cfg = FEEDS[selected_cat][provider_name]
        raw_entries = fetch_feed(provider_cfg["url"])
        deck_data[provider_name] = []
        
        for entry in raw_entries:
            item = {
                "title": entry.get("title", "Advisory Notice"),
                "link": entry.get("link", "#"),
                "summary": clean_summary_text(entry.get("summary", ""), 160),
                "entry_obj": entry
            }
            deck_data[provider_name].append(item)
            raw_context_lines.append(f"[{provider_name}] {item['title']}: {item['summary']}")

# --- Action & Intelligence Bar ---
with st.popover("💬 Ask CJ", use_container_width=False):
    st.markdown("#### 🛡️ Ask Cyber Journal (CJ)")
    
    for msg in st.session_state["cj_chat_history"][-6:]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    with st.form("cj_query_form", clear_on_submit=True):
        user_question = st.text_input("Ask CJ:", placeholder="e.g., Any actively exploited VPN flaws today?")
        submitted = st.form_submit_button("Submit", use_container_width=True)
        
        if submitted and user_question:
            st.session_state["cj_chat_history"].append({"role": "user", "content": user_question})
            context_blob = "\n".join(raw_context_lines[:40])
            with st.spinner("CJ is analyzing intelligence feeds..."):
                answer = ask_cj_analyst(user_question, context_blob, api_key_to_use)
                st.session_state["cj_chat_history"].append({"role": "assistant", "content": answer})
                st.rerun()

# --- Multi-Column Intelligence Deck ---
if not active_providers:
    st.info("Select at least one feed provider in the sidebar to activate the deck.")
else:
    deck_columns = st.columns(len(active_providers))

    for col, provider_name in zip(deck_columns, active_providers):
        provider_cfg = FEEDS[selected_cat][provider_name]
        badge_color = provider_cfg["color"]
        badge_bg = provider_cfg["bg"]
        items = deck_data.get(provider_name, [])
        count_label = f"{len(items)} items" if items else "Offline / Timeout"
        
        with col:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding: 0 4px;">
                <span style="font-weight:700; font-size:14px; color:#F1F5F9; letter-spacing:0.3px;">{provider_name}</span>
                <span style="background:{badge_bg}; color:{badge_color}; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:12px; font-family:monospace;">
                    {count_label}
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.container(height=720, border=True):
                if not items:
                    st.markdown("<p style='color:#64748B; font-size:13px;'>No advisories available or firewall blocked access.</p>", unsafe_allow_html=True)
                else:
                    for item in items:
                        headline = html.escape(item["title"])
                        link = item["link"]
                        snippet = html.escape(item["summary"])
                        rel_time = format_relative_time(item["entry_obj"])

                        card_html = f'<a href="{link}" target="_blank" class="card-link-wrapper"><div class="threat-card"><div class="card-meta"><span class="card-time">{rel_time}</span></div><div class="card-title">{headline}</div><div class="card-snippet">{snippet}</div></div></a>'
                        st.markdown(card_html, unsafe_allow_html=True)