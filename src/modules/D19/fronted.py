import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
API_URL=os.getenv(API_URL)
st.set_page_config(
    page_title="DrugDrug Interaction System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API_URL = "http://127.0.0.1:8000"

# ──────────────────────────────────────────────────────────────────────
# GLOBAL CSS  – vibrant medical-tech palette
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
.top-banner::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(0,240,255,.18), transparent);
    pointer-events: none;
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
    text-shadow: none;
}
.banner-sub {
    font-size: .92rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase;
}

/* ── Nav bar ── */
.nav-bar {
    display: flex; gap: 6px;
    background: #0d0f1a;
    padding: 12px 40px;
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 999;
}
.nav-btn {
    padding: 9px 26px; border-radius: 50px; border: 1.5px solid var(--border);
    font-size: .88rem; font-weight: 700; cursor: pointer; letter-spacing: .5px;
    transition: all .2s; background: transparent; color: var(--muted);
    text-transform: uppercase;
}
.nav-btn:hover  { border-color: var(--accent1); color: var(--accent1); background: rgba(0,240,255,.07); }
.nav-btn.active { border-color: var(--accent2); color: var(--accent2); background: rgba(168,85,247,.15); }

/* ── Section wrapper ── */
.section { padding: 32px 40px; max-width: 1400px; margin: 0 auto; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 32px;
    transition: border-color .2s, box-shadow .2s;
}
.card:hover { border-color: rgba(0,240,255,.35); box-shadow: 0 0 24px rgba(0,240,255,.08); }

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 18px; margin-bottom: 32px; }
.stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px; text-align: center;
    position: relative; overflow: hidden;
    transition: transform .2s, box-shadow .2s;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,.4); }
.stat-card::before {
    content: ''; position: absolute; inset: 0;
    background: var(--glow);
    opacity: .07; pointer-events: none;
}
.stat-number {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.4rem; font-weight: 900;
    background: var(--grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 6px;
}
.stat-label { font-size: .82rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.stat-icon  { font-size: 2rem; margin-bottom: 8px; display: block; }

/* ── Section headings ── */
.sec-heading {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.15rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.sec-heading span { color: var(--accent1); }

/* ── Result boxes ── */
.result-major   { background:#1a0505; border:1px solid #ef4444; border-radius:12px; padding:18px 22px; }
.result-moderate{ background:#1a1005; border:1px solid #f97316; border-radius:12px; padding:18px 22px; }
.result-minor   { background:#0a1a10; border:1px solid #22c55e; border-radius:12px; padding:18px 22px; }
.result-none    { background:#0a1020; border:1px solid var(--accent1); border-radius:12px; padding:18px 22px; }
.result-row     { display:flex; gap:10px; align-items:center; margin-bottom:6px; }
.badge {
    display:inline-block; padding:3px 12px; border-radius:50px;
    font-size:.78rem; font-weight:800; letter-spacing:1px; text-transform:uppercase;
}
.badge-major    { background:#ef4444; color:#fff; }
.badge-moderate { background:#f97316; color:#fff; }
.badge-minor    { background:#22c55e; color:#fff; }
.badge-safe     { background:#00f0ff; color:#0d0f1a; }

/* ── Alternative box ── */
.alt-box {
    background: linear-gradient(135deg, #0f1f2a, #1a0f2a);
    border: 1px solid var(--accent2); border-radius: 14px; padding: 20px 26px;
    margin-top: 10px;
}
.alt-drug { font-size:1.3rem; font-weight:800; color: var(--accent2); margin-bottom:4px; }
.alt-reason { font-size:.88rem; color: var(--muted); }

/* ── Streamlit widget overrides ── */
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > div > input {
    background: #1e2235 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
div[data-testid="stSelectbox"] > div:focus-within,
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 2px rgba(0,240,255,.2) !important;
}
label[data-testid="stWidgetLabel"] p { color: #94a3b8 !important; font-weight: 700 !important; font-size:.82rem !important; letter-spacing:1px; text-transform:uppercase; }
.stButton > button {
    background: linear-gradient(90deg, var(--accent2), var(--accent1)) !important;
    color: #0d0f1a !important; font-weight: 800 !important;
    border: none !important; border-radius: 50px !important;
    padding: 10px 32px !important; font-size:.88rem !important;
    letter-spacing: 1px; text-transform: uppercase;
    transition: opacity .2s, transform .2s !important;
    box-shadow: 0 4px 20px rgba(168,85,247,.3) !important;
}
.stButton > button:hover { opacity:.9 !important; transform: translateY(-2px) !important; }
div[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; }

/* ── SQL / Procedure blocks ── */
.sql-block {
    background: #0a0d18;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent1);
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-family: 'Courier New', monospace !important;
    font-size: .82rem;
    color: #93c5fd;
    overflow-x: auto;
    white-space: pre;
    line-height: 1.7;
}
.proc-block {
    background: #0a0d18;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent2);
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin-bottom: 18px;
    font-family: 'Courier New', monospace !important;
    font-size: .82rem;
    color: #d8b4fe;
    overflow-x: auto;
    white-space: pre;
    line-height: 1.7;
}
.q-label {
    background: linear-gradient(90deg, #1e1b4b, #0d0f1a);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 18px;
    font-size:.85rem; font-weight:700; color: var(--accent2);
    margin-bottom:8px; display:flex; align-items:center; gap:8px;
}
.divider { height:1px; background: var(--border); margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_drug_list():
    try:
        r = requests.get(f"{API_URL}/drugs", timeout=5)
        return [d["name"] for d in r.json()]
    except Exception:
        return []

@st.cache_data(ttl=30)
def get_counts():
    try:
        return requests.get(f"{API_URL}/dashboard/counts", timeout=5).json()
    except Exception:
        return {"drugs": 0, "interactions": 0, "alerts": 0, "alternatives": 0}

@st.cache_data(ttl=60)
def get_all_drugs():
    try:
        return requests.get(f"{API_URL}/drugs/all", timeout=5).json()
    except Exception:
        return []

def severity_badge(s):
    cls = {"Major": "badge-major", "Moderate": "badge-moderate", "Minor": "badge-minor"}.get(s, "badge-safe")
    return f'<span class="badge {cls}">{s}</span>'

# ──────────────────────────────────────────────────────────────────────
# SESSION STATE – active page
# ──────────────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "Interaction"

# ──────────────────────────────────────────────────────────────────────
# TOP BANNER
# ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="top-banner">
  <div class="banner-title">💊 DrugDrug Interaction</div>
  <div class="banner-sub">Advanced Pharmacological Safety System</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# NAV BAR  (Streamlit columns trick)
# ──────────────────────────────────────────────────────────────────────

pages = ["Dashboard", "Interaction", "SQL Queries", "Procedures"]
icons = {"Dashboard": "📊", "Interaction": "🔬", "SQL Queries": "🗄️", "Procedures": "⚙️"}

nav_cols = st.columns(len(pages) + 4)
for i, p in enumerate(pages):
    with nav_cols[i + 2]:
        label = f"{icons[p]}  {p}"
        if st.button(label, key=f"nav_{p}"):
            st.session_state.page = p

page = st.session_state.page

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

drug_list = get_drug_list()

# ──────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ──────────────────────────────────────────────────────────────────────

if page == "Dashboard":
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown('<div class="sec-heading">📊 <span>System Overview</span></div>', unsafe_allow_html=True)

    counts = get_counts()

    stat_cfgs = [
        {"label": "Total Drugs",       "key": "drugs",        "icon": "💊",
         "grad": "linear-gradient(90deg,#00f0ff,#38bdf8)",   "glow": "#00f0ff"},
        {"label": "Interactions",      "key": "interactions", "icon": "⚡",
         "grad": "linear-gradient(90deg,#a855f7,#ec4899)",   "glow": "#a855f7"},
        {"label": "Alerts Triggered",  "key": "alerts",       "icon": "🚨",
         "grad": "linear-gradient(90deg,#ef4444,#f97316)",   "glow": "#ef4444"},
        {"label": "Alternatives",      "key": "alternatives", "icon": "🔄",
         "grad": "linear-gradient(90deg,#22c55e,#84cc16)",   "glow": "#22c55e"},
    ]

    stat_html = '<div class="stat-grid">'
    for cfg in stat_cfgs:
        val = counts.get(cfg["key"], 0)
        stat_html += f"""
        <div class="stat-card" style="--glow:{cfg['glow']};--grad:{cfg['grad']}">
          <span class="stat-icon">{cfg['icon']}</span>
          <span class="stat-number">{val:,}</span>
          <span class="stat-label">{cfg['label']}</span>
        </div>"""
    stat_html += "</div>"
    st.markdown(stat_html, unsafe_allow_html=True)

    # ── Full drug table ──
    st.markdown('<div class="sec-heading">💊 <span>Complete Drug Database</span></div>', unsafe_allow_html=True)
    all_drugs = get_all_drugs()
    if all_drugs:
        df = pd.DataFrame(all_drugs)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name":        st.column_config.TextColumn("Drug Name",    width="medium"),
                "class":       st.column_config.TextColumn("Drug Class",   width="medium"),
                "description": st.column_config.TextColumn("Description",  width="large"),
            }
        )
    else:
        st.info("No drug data available.")

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# PAGE: INTERACTION
# ──────────────────────────────────────────────────────────────────────

elif page == "Interaction":
    st.markdown('<div class="section">', unsafe_allow_html=True)

    # ── Drug Interaction Checker ──
    st.markdown('<div class="sec-heading">🔬 <span>Drug Interaction Checker</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 💊 First Drug")
        drug1_text = st.text_input("Type drug name", key="d1_text", placeholder="e.g. Aspirin")
        drug1_sel  = st.selectbox("Or select from list", options=[""] + drug_list, key="d1_sel")
        drug1 = drug1_sel if drug1_sel else drug1_text
        if drug1:
            st.markdown(f'<span class="badge badge-safe">{drug1}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 💊 Second Drug")
        drug2_text = st.text_input("Type drug name", key="d2_text", placeholder="e.g. Warfarin")
        drug2_sel  = st.selectbox("Or select from list", options=[""] + drug_list, key="d2_sel")
        drug2 = drug2_sel if drug2_sel else drug2_text
        if drug2:
            st.markdown(f'<span class="badge badge-safe">{drug2}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    check_col, _ = st.columns([1, 3])
    with check_col:
        check_clicked = st.button("🔍 Check Interaction", key="check_btn")

    if check_clicked:
        if drug1 and drug2:
            with st.spinner("Analyzing interaction…"):
                try:
                    resp   = requests.post(f"{API_URL}/check-interaction",
                                           json={"drug1": drug1, "drug2": drug2}, timeout=5)
                    result = resp.json()

                    if result.get("interaction"):
                        sev = result["severity"]
                        box_cls = {"Major": "result-major", "Moderate": "result-moderate"}.get(sev, "result-minor")
                        st.markdown(f"""
                        <div class="{box_cls}" style="margin-top:16px">
                          <div class="result-row">
                            <span style="font-size:1.5rem">⚠️</span>
                            <strong style="font-size:1.1rem">Interaction Detected!</strong>
                            {severity_badge(sev)}
                          </div>
                          <div style="margin:8px 0;font-size:.9rem;color:#cbd5e1">
                            <b>Mechanism:</b> {result.get('mechanism','N/A')}
                          </div>
                          <div style="font-size:.9rem;color:#cbd5e1">
                            <b>Recommendation:</b> {result.get('recommendation','N/A')}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="result-none" style="margin-top:16px">
                          <div class="result-row">
                            <span style="font-size:1.5rem">✅</span>
                            <strong style="font-size:1.1rem">No Interaction Found</strong>
                            <span class="badge badge-safe">SAFE</span>
                          </div>
                          <p style="margin:6px 0 0;font-size:.88rem;color:#94a3b8">
                            No documented interaction between these two drugs in the database.
                          </p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"API Error: {e}")
        else:
            st.warning("⚠️ Please select or type both drug names.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Alert History ──
    st.markdown('<div class="sec-heading">🚨 <span>Alert History for This Drug Pair</span></div>',
                unsafe_allow_html=True)

    alert_col, _ = st.columns([1, 3])
    with alert_col:
        show_alerts = st.button("📋 Show Alert History", key="alerts_btn")

    if show_alerts:
        if drug1 and drug2:
            try:
                resp   = requests.get(f"{API_URL}/alerts/{drug1}/{drug2}", timeout=5)
                alerts = resp.json()
                if alerts:
                    df = pd.DataFrame(alerts)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No alert history found for this drug combination.")
            except Exception as e:
                st.error(f"API Error: {e}")
        else:
            st.warning("Please select both drugs first.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Alternative Drug Finder ──
    st.markdown('<div class="sec-heading">🔄 <span>Alternative Drug Finder</span></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    alt_col1, alt_col2 = st.columns([2, 1])

    with alt_col1:
        alt_text = st.text_input("Type drug name for alternative", key="alt_text",
                                  placeholder="e.g. Aspirin")
        alt_sel  = st.selectbox("Or select from full drug list",
                                 options=[""] + drug_list, key="alt_sel")
        alt_drug = alt_sel if alt_sel else alt_text

    with alt_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        find_alt = st.button("💡 Find Alternative", key="alt_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    if find_alt:
        if alt_drug:
            with st.spinner("Searching alternatives…"):
                try:
                    resp   = requests.get(f"{API_URL}/alternatives/{alt_drug}", timeout=5)
                    result = resp.json()
                    if "alternative" in result:
                        st.markdown(f"""
                        <div class="alt-box">
                          <div style="font-size:.78rem;color:var(--muted);text-transform:uppercase;
                                      letter-spacing:1.5px;margin-bottom:6px">Alternative for <b>{result['drug']}</b></div>
                          <div class="alt-drug">💊 {result['alternative']}</div>
                          <div class="alt-reason">📝 {result['reason']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No alternative found for this drug.")
                except Exception as e:
                    st.error(f"API Error: {e}")
        else:
            st.warning("Please enter or select a drug name.")

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# PAGE: SQL QUERIES
# ──────────────────────────────────────────────────────────────────────

elif page == "SQL Queries":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-heading">🗄️ <span>SQL Queries for Drug Interaction System</span></div>',
                unsafe_allow_html=True)

    sql_items = [
        ("Get all drugs", """SELECT drug_id, name, class, description
FROM drugs
ORDER BY name ASC;"""),

        ("Get all interactions with severity", """SELECT i.interaction_id, d1.name AS drug1, d2.name AS drug2,
       i.severity, i.mechanism, i.recommendation
FROM interactions i
JOIN drugs d1 ON i.drug1_id = d1.drug_id
JOIN drugs d2 ON i.drug2_id = d2.drug_id
ORDER BY i.severity DESC;"""),

        ("Check interaction between two specific drugs", """SELECT i.severity, i.mechanism, i.recommendation
FROM interactions i
JOIN drugs d1 ON i.drug1_id = d1.drug_id
JOIN drugs d2 ON i.drug2_id = d2.drug_id
WHERE (d1.name = 'Aspirin'  AND d2.name = 'Warfarin')
   OR (d1.name = 'Warfarin' AND d2.name = 'Aspirin');"""),

        ("Get all Major severity interactions", """SELECT d1.name AS drug1, d2.name AS drug2,
       i.mechanism, i.recommendation
FROM interactions i
JOIN drugs d1 ON i.drug1_id = d1.drug_id
JOIN drugs d2 ON i.drug2_id = d2.drug_id
WHERE i.severity = 'Major'
ORDER BY d1.name;"""),

        ("Get all alerts for a drug pair", """SELECT a.alert_id, d1.name AS drug1, d2.name AS drug2,
       a.severity, a.message, a.timestamp
FROM alerts a
JOIN drugs d1 ON a.drug1_id = d1.drug_id
JOIN drugs d2 ON a.drug2_id = d2.drug_id
WHERE (d1.name = 'Aspirin'  AND d2.name = 'Warfarin')
   OR (d1.name = 'Warfarin' AND d2.name = 'Aspirin')
ORDER BY a.timestamp DESC;"""),

        ("Count interactions by severity", """SELECT severity, COUNT(*) AS total_interactions
FROM interactions
GROUP BY severity
ORDER BY total_interactions DESC;"""),

        ("Find alternative drug", """SELECT d.name AS original_drug,
       alt.name AS alternative_drug,
       a.reason
FROM alternatives a
JOIN drugs d   ON a.drug_id      = d.drug_id
JOIN drugs alt ON a.alt_drug_id  = alt.drug_id
WHERE d.name = 'Aspirin';"""),

        ("Top 10 drugs involved in most interactions", """SELECT d.name, COUNT(*) AS interaction_count
FROM (
    SELECT drug1_id AS drug_id FROM interactions
    UNION ALL
    SELECT drug2_id AS drug_id FROM interactions
) combined
JOIN drugs d ON combined.drug_id = d.drug_id
GROUP BY d.name
ORDER BY interaction_count DESC
LIMIT 10;"""),

        ("All alerts ordered by timestamp", """SELECT a.alert_id,
       d1.name AS drug1, d2.name AS drug2,
       a.severity, a.message,
       FORMAT(a.timestamp, 'yyyy-MM-dd HH:mm:ss') AS alert_time
FROM alerts a
JOIN drugs d1 ON a.drug1_id = d1.drug_id
JOIN drugs d2 ON a.drug2_id = d2.drug_id
ORDER BY a.timestamp DESC;"""),

        ("Drugs that have NO alternatives recorded", """SELECT d.name
FROM drugs d
LEFT JOIN alternatives a ON d.drug_id = a.drug_id
WHERE a.drug_id IS NULL
ORDER BY d.name;"""),
    ]

    for i, (title, sql) in enumerate(sql_items, 1):
        st.markdown(f'<div class="q-label">🔷 Q{i}. {title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-block">{sql}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# PAGE: PROCEDURES
# ──────────────────────────────────────────────────────────────────────

elif page == "Procedures":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-heading">⚙️ <span>Stored Procedures</span></div>',
                unsafe_allow_html=True)

    procedures = [
        ("Check Drug Interaction Procedure", """DELIMITER $$

CREATE PROCEDURE CheckDrugInteraction(
    IN  p_drug1   VARCHAR(100),
    IN  p_drug2   VARCHAR(100),
    OUT p_found   TINYINT,
    OUT p_severity VARCHAR(20),
    OUT p_mechanism TEXT,
    OUT p_recommendation TEXT
)
BEGIN
    -- Lookup interaction in both directions
    SELECT i.severity, i.mechanism, i.recommendation
    INTO   p_severity, p_mechanism, p_recommendation
    FROM   interactions i
    JOIN   drugs d1 ON i.drug1_id = d1.drug_id
    JOIN   drugs d2 ON i.drug2_id = d2.drug_id
    WHERE  (d1.name = p_drug1 AND d2.name = p_drug2)
       OR  (d1.name = p_drug2 AND d2.name = p_drug1)
    LIMIT 1;

    IF FOUND_ROWS() > 0 THEN
        SET p_found = 1;

        -- Auto-log the alert
        INSERT INTO alerts (drug1_id, drug2_id, severity, message, timestamp)
        SELECT d1.drug_id, d2.drug_id,
               p_severity,
               CONCAT('Interaction detected: ', p_drug1, ' + ', p_drug2),
               NOW()
        FROM   drugs d1, drugs d2
        WHERE  d1.name = p_drug1 AND d2.name = p_drug2;
    ELSE
        SET p_found = 0;
    END IF;
END$$

DELIMITER ;

-- Usage:
CALL CheckDrugInteraction('Aspirin', 'Warfarin', @found, @sev, @mech, @rec);
SELECT @found, @sev, @mech, @rec;"""),

        ("Get All Alerts for Drug Pair", """DELIMITER $$

CREATE PROCEDURE GetAlertsForPair(
    IN p_drug1 VARCHAR(100),
    IN p_drug2 VARCHAR(100)
)
BEGIN
    SELECT a.alert_id,
           d1.name          AS drug1,
           d2.name          AS drug2,
           a.severity,
           a.message,
           a.timestamp
    FROM   alerts a
    JOIN   drugs d1 ON a.drug1_id = d1.drug_id
    JOIN   drugs d2 ON a.drug2_id = d2.drug_id
    WHERE  (d1.name = p_drug1 AND d2.name = p_drug2)
       OR  (d1.name = p_drug2 AND d2.name = p_drug1)
    ORDER BY a.timestamp DESC;
END$$

DELIMITER ;

-- Usage:
CALL GetAlertsForPair('Aspirin', 'Warfarin');"""),

        ("Find Alternative Drug Procedure", """DELIMITER $$

CREATE PROCEDURE FindAlternativeDrug(
    IN p_drug VARCHAR(100)
)
BEGIN
    SELECT  d_orig.name  AS original_drug,
            d_alt.name   AS alternative_drug,
            a.reason
    FROM    alternatives a
    JOIN    drugs d_orig ON a.drug_id     = d_orig.drug_id
    JOIN    drugs d_alt  ON a.alt_drug_id = d_alt.drug_id
    WHERE   d_orig.name = p_drug
    LIMIT   1;

    IF ROW_COUNT() = 0 THEN
        SELECT 'No alternative found' AS message;
    END IF;
END$$

DELIMITER ;

-- Usage:
CALL FindAlternativeDrug('Aspirin');"""),

        ("Get Severity Breakdown Procedure", """DELIMITER $$

CREATE PROCEDURE GetSeverityBreakdown()
BEGIN
    SELECT  severity,
            COUNT(*)                              AS total,
            ROUND(COUNT(*) * 100.0
                  / (SELECT COUNT(*) FROM interactions), 2) AS percentage
    FROM    interactions
    GROUP BY severity
    ORDER BY FIELD(severity, 'Major', 'Moderate', 'Minor');
END$$

DELIMITER ;

-- Usage:
CALL GetSeverityBreakdown();"""),

        ("Dashboard Counts Procedure", """DELIMITER $$

CREATE PROCEDURE GetDashboardCounts()
BEGIN
    SELECT
        (SELECT COUNT(*) FROM drugs)         AS total_drugs,
        (SELECT COUNT(*) FROM interactions)  AS total_interactions,
        (SELECT COUNT(*) FROM alerts)        AS total_alerts,
        (SELECT COUNT(*) FROM alternatives)  AS total_alternatives;
END$$

DELIMITER ;

-- Usage:
CALL GetDashboardCounts();"""),

        ("Top 10 Most Interacting Drugs", """DELIMITER $$

CREATE PROCEDURE GetTopInteractingDrugs(
    IN p_limit INT
)
BEGIN
    SELECT  d.name           AS drug_name,
            COUNT(*)         AS interaction_count
    FROM (
        SELECT drug1_id AS drug_id FROM interactions
        UNION ALL
        SELECT drug2_id AS drug_id FROM interactions
    ) combined
    JOIN    drugs d ON combined.drug_id = d.drug_id
    GROUP BY d.name
    ORDER BY interaction_count DESC
    LIMIT   p_limit;
END$$

DELIMITER ;

-- Usage:
CALL GetTopInteractingDrugs(10);"""),
    ]

    for i, (title, proc) in enumerate(procedures, 1):
        st.markdown(f'<div class="q-label">⚙️ Procedure {i}: {title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="proc-block">{proc}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
