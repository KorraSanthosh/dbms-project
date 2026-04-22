import streamlit as st
import pandas as pd
from pymongo import MongoClient
import datetime

# ──────────────────────────────────────────────────────────────────────
# PAGE CONFIG & MONGODB SETUP
# ──────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="DrugDrug Interaction System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Connect to MongoDB directly using Streamlit Secrets for security
@st.cache_resource
def init_connection():
    try:
        uri = st.secrets["MONGODB_URI"]
        return MongoClient(uri)
    except Exception as e:
        st.error("Missing MONGODB_URI in Streamlit Secrets!")
        return None

client = init_connection()
if client:
    db = client["drug_interaction_system"]
    drugs_col = db["drugs"]
    interactions_col = db["interactions"]
    alternatives_col = db["alternatives"]
    alerts_col = db["alerts"]

# ──────────────────────────────────────────────────────────────────────
# GLOBAL CSS – Vibrant Medical-Tech Palette
# ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Nunito:wght@400;600;700;800&display=swap');

/* ── Root palette ── */
:root {
    --bg:       #0d0f1a;
    --card:     #161929;
    --border:   #2a2f4a;
    --accent1:  #00f0ff;   /* cyan   */
    --accent2:  #a855f7;   /* violet */
    --accent3:  #f97316;   /* orange */
    --accent4:  #22c55e;   /* green  */
    --accent5:  #ef4444;   /* red    */
    --text:     #e2e8f0;
    --muted:    #64748b;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main { background: var(--bg) !important; color: var(--text) !important; }
[data-testid="stHeader"] { background: transparent !important; }
* { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── Top banner ── */
.top-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
    border-bottom: 2px solid var(--accent1);
    padding: 24px 40px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    margin-bottom: 0;
    position: relative;
    overflow: hidden;
}
.banner-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.1;
}
.banner-sub {
    font-size: .92rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase;
}

/* ── Section wrapper ── */
.section { padding: 32px 40px; max-width: 1400px; margin: 0 auto; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 32px;
}

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 18px; margin-bottom: 32px; }
.stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px; text-align: center;
}
.stat-number {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.4rem; font-weight: 900;
    color: var(--accent1);
}
.stat-label { font-size: .82rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }

/* ── Result boxes ── */
.result-major   { background:#1a0505; border:1px solid #ef4444; border-radius:12px; padding:18px 22px; }
.result-moderate{ background:#1a1005; border:1px solid #f97316; border-radius:12px; padding:18px 22px; }
.result-minor   { background:#0a1a10; border:1px solid #22c55e; border-radius:12px; padding:18px 22px; }
.result-none    { background:#0a1020; border:1px solid var(--accent1); border-radius:12px; padding:18px 22px; }
.badge {
    display:inline-block; padding:3px 12px; border-radius:50px;
    font-size:.78rem; font-weight:800; letter-spacing:1px; text-transform:uppercase;
}
.badge-major    { background:#ef4444; color:#fff; }
.badge-moderate { background:#f97316; color:#fff; }
.badge-minor    { background:#22c55e; color:#fff; }
.badge-safe     { background:#00f0ff; color:#0d0f1a; }

.divider { height:1px; background: var(--border); margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# HELPERS (Direct MongoDB Logic)
# ──────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_drug_list():
    try:
        return [d["name"] for d in drugs_col.find({}, {"_id": 0})]
    except: return []

@st.cache_data(ttl=30)
def get_counts():
    try:
        return {
            "drugs": drugs_col.count_documents({}),
            "interactions": interactions_col.count_documents({}),
            "alerts": alerts_col.count_documents({}),
            "alternatives": alternatives_col.count_documents({}),
        }
    except: return {"drugs": 0, "interactions": 0, "alerts": 0, "alternatives": 0}

@st.cache_data(ttl=60)
def get_all_drugs():
    try: return list(drugs_col.find({}, {"_id": 0}))
    except: return []

def severity_badge(s):
    cls = {"Major": "badge-major", "Moderate": "badge-moderate", "Minor": "badge-minor"}.get(s, "badge-safe")
    return f'<span class="badge {cls}">{s}</span>'

# ──────────────────────────────────────────────────────────────────────
# UI LOGIC
# ──────────────────────────────────────────────────────────────────────

if "page" not in st.session_state: st.session_state.page = "Interaction"

st.markdown("""
<div class="top-banner">
  <div class="banner-title">💊 Drug Interaction</div>
  <div class="banner-sub">Advanced Pharmacological Safety System</div>
</div>
""", unsafe_allow_html=True)

pages = ["Dashboard", "Interaction", "SQL Queries"]
nav_cols = st.columns(len(pages) + 4)
for i, p in enumerate(pages):
    with nav_cols[i + 2]:
        if st.button(p): st.session_state.page = p

page = st.session_state.page
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

drug_list = get_drug_list()

if page == "Dashboard":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    counts = get_counts()
    stat_html = '<div class="stat-grid">'
    for label, key in [("Total Drugs", "drugs"), ("Interactions", "interactions"), ("Alerts", "alerts"), ("Alternatives", "alternatives")]:
        stat_html += f'<div class="stat-card"><div class="stat-number">{counts.get(key, 0)}</div><div class="stat-label">{label}</div></div>'
    stat_html += '</div>'
    st.markdown(stat_html, unsafe_allow_html=True)
    
    st.markdown("### 💊 Complete Drug Database")
    st.dataframe(pd.DataFrame(get_all_drugs()), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Interaction":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        d1 = st.selectbox("Select First Drug", [""] + drug_list, key="d1")
    with col2:
        d2 = st.selectbox("Select Second Drug", [""] + drug_list, key="d2")
    
    if st.button("🔍 Check Interaction"):
        if d1 and d2:
            res = interactions_col.find_one({"$or": [{"drug1": d1, "drug2": d2}, {"drug1": d2, "drug2": d1}]})
            if res:
                box = "result-major" if res["severity"] == "Major" else "result-moderate"
                st.markdown(f'<div class="{box}"><h4>⚠️ Interaction Detected!</h4>{severity_badge(res["severity"])}<br><p>{res.get("mechanism", "")}</p></div>', unsafe_allow_html=True)
                # Auto-log alert
                alerts_col.insert_one({"drug1": d1, "drug2": d2, "severity": res["severity"], "timestamp": datetime.datetime.now(), "message": "Interaction detected"})
            else:
                st.markdown('<div class="result-none">✅ No Interaction Found. Safe!</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "SQL Queries":
    st.markdown('<div class="section"><h3>🗄️ SQL Query Reference</h3>', unsafe_allow_html=True)
    st.code("SELECT * FROM drugs ORDER BY name ASC;", language="sql")
    st.code("SELECT * FROM interactions WHERE severity = 'Major';", language="sql")
    st.markdown('</div>', unsafe_allow_html=True)
