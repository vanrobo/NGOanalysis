import streamlit as st
import pandas as pd
from groq import Groq
import os, re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="NGO COMMAND CENTER",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── MONOCHROME DESIGN SYSTEM ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

*, *::before, *::after { font-family: 'Space Mono', monospace !important; box-sizing: border-box; }
html, body { background: #050505; color: #e0e0e0; }
.stApp { background: #050505; }
.main .block-container { background: #050505; padding: 1.5rem 2rem 3rem 2rem; max-width: 100%; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #000 !important;
    border-right: 1px solid #1c1c1c;
    min-width: 210px !important; max-width: 210px !important;
}
section[data-testid="stSidebar"] > div { padding: 1.4rem 1rem; }
section[data-testid="stSidebar"] * { color: #c0c0c0 !important; }
section[data-testid="stSidebar"] .stRadio > label {
    font-size: 9px !important; letter-spacing: 3px !important;
    color: #333 !important; text-transform: uppercase; margin-bottom: 8px; display: block;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    font-size: 12px !important; color: #666 !important;
    padding: 6px 0 6px 10px; border-left: 2px solid transparent; margin: 2px 0;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    color: #f0f0f0 !important; border-left: 2px solid #f0f0f0 !important;
}
section[data-testid="stSidebar"] .stFileUploader label {
    font-size: 9px !important; letter-spacing: 2px !important;
    color: #333 !important; text-transform: uppercase;
}
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: #0a0a0a !important; border: 1px dashed #2a2a2a !important; border-radius: 0 !important;
}
section[data-testid="stSidebar"] hr { border-color: #1c1c1c; margin: 1rem 0; }

/* Inputs */
.stSelectbox > label, .stTextInput > label, .stNumberInput > label,
.stSlider > label, .stMultiSelect > label, .stCheckbox > label, .stTextArea > label {
    font-size: 9px !important; letter-spacing: 2px !important;
    color: #444 !important; text-transform: uppercase !important;
}
.stSelectbox [data-baseweb="select"] > div, .stTextInput input,
.stNumberInput input, .stTextArea textarea {
    background: #0c0c0c !important; border: 1px solid #222 !important;
    border-radius: 0 !important; color: #e0e0e0 !important; font-size: 12px !important;
}
[data-baseweb="popover"] { background: #111 !important; border: 1px solid #222 !important; }
[data-baseweb="menu"] { background: #111 !important; }
[data-baseweb="menu"] li { color: #c0c0c0 !important; font-size: 12px !important; }
[data-baseweb="menu"] li:hover { background: #1c1c1c !important; }
[data-baseweb="tag"] {
    background: #1a1a1a !important; border: 1px solid #333 !important; border-radius: 0 !important;
}
[data-baseweb="tag"] span { color: #c0c0c0 !important; font-size: 11px !important; }

/* Buttons */
.stButton > button {
    background: #0c0c0c !important; border: 1px solid #2a2a2a !important;
    color: #888 !important; border-radius: 0 !important;
    font-size: 10px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; padding: 8px 18px !important;
}
.stButton > button:hover {
    background: #1a1a1a !important; border-color: #666 !important; color: #e0e0e0 !important;
}
.stButton > button[kind="primary"] {
    background: #e0e0e0 !important; border-color: #e0e0e0 !important; color: #050505 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #fff !important; border-color: #fff !important;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: #0a0a0a; border: 1px solid #1c1c1c; border-radius: 0; padding: 14px;
}
div[data-testid="metric-container"] label {
    font-size: 9px !important; letter-spacing: 2px !important;
    color: #444 !important; text-transform: uppercase !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 1.7em !important; color: #e0e0e0 !important;
}
div[data-testid="metric-container"] [data-testid="metric-delta"] { font-size: 10px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #000 !important; border-bottom: 1px solid #1c1c1c !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #444 !important; border-radius: 0 !important;
    font-size: 10px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #e0e0e0 !important; border-bottom: 2px solid #e0e0e0 !important; background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { background: #050505 !important; padding-top: 20px !important; }

/* DataFrames */
.stDataFrame { border: 1px solid #1c1c1c !important; border-radius: 0 !important; }

/* Chat */
[data-testid="stChatMessage"] {
    background: #0a0a0a !important; border: 1px solid #1c1c1c !important; border-radius: 0 !important;
}
[data-testid="stChatInput"] > div {
    background: #0a0a0a !important; border: 1px solid #222 !important; border-radius: 0 !important;
}
[data-testid="stChatInput"] textarea { background: transparent !important; color: #e0e0e0 !important; }

/* Custom components */
.mono-title {
    font-size: 16px; font-weight: 700; color: #e0e0e0;
    letter-spacing: 4px; text-transform: uppercase; margin-bottom: 2px;
}
.mono-sub { font-size: 10px; color: #333; letter-spacing: 1px; margin-bottom: 20px; }
.sec-label {
    font-size: 9px; letter-spacing: 3px; color: #2a2a2a; text-transform: uppercase;
    border-bottom: 1px solid #111; padding-bottom: 7px; margin: 24px 0 14px 0;
}
.stat-block {
    background: #0a0a0a; border: 1px solid #1c1c1c; padding: 16px; margin-bottom: 1px;
}
.stat-block .val { font-size: 26px; font-weight: 700; color: #e0e0e0; display: block; }
.stat-block .lbl { font-size: 9px; letter-spacing: 2px; color: #444; text-transform: uppercase; margin-top: 2px; display: block; }
.stat-block .sub { font-size: 10px; color: #2a2a2a; margin-top: 4px; display: block; }
.info-line {
    background: #0a0a0a; border: 1px solid #1c1c1c; border-left: 2px solid #555;
    padding: 9px 13px; font-size: 11px; color: #666; margin: 8px 0;
}
.warn-line {
    background: #0a0a0a; border: 1px solid #1c1c1c; border-left: 2px solid #333;
    padding: 9px 13px; font-size: 11px; color: #444; margin: 8px 0;
}
.ai-block {
    background: #080808; border: 1px solid #1c1c1c;
    padding: 20px 24px; margin-top: 14px;
    line-height: 1.85; color: #bbb; font-size: 12px;
}
.hr { border: none; border-top: 1px solid #111; margin: 22px 0; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def section(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)

def info(msg):
    st.markdown(f'<div class="info-line">{msg}</div>', unsafe_allow_html=True)

def warn(msg):
    st.markdown(f'<div class="warn-line">{msg}</div>', unsafe_allow_html=True)

# ─── NEIGHBORHOOD COORDS (Delhi) ─────────────────────────────────────────────
NBHD_COORDS = {
    'Paschim Vihar':   (28.6685, 77.0946),
    'Rohini':          (28.7045, 77.1100),
    'Dwarka':          (28.5921, 77.0460),
    'Janakpuri':       (28.6280, 77.0820),
    'Pitampura':       (28.7031, 77.1300),
    'Saket':           (28.5220, 77.2090),
    'Lajpat Nagar':    (28.5707, 77.2430),
    'Karol Bagh':      (28.6507, 77.1910),
    'Vasant Kunj':     (28.5226, 77.1590),
    'Connaught Place': (28.6315, 77.2195),
}
MOCK_AREAS = list(NBHD_COORDS.keys())

# ─── PLOTLY MONO BASE ─────────────────────────────────────────────────────────
import plotly.graph_objects as go
import plotly.express as px

PBASE = dict(
    paper_bgcolor='#050505', plot_bgcolor='#050505',
    font=dict(family='Space Mono', color='#555', size=10),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(gridcolor='#0f0f0f', linecolor='#1c1c1c', tickcolor='#2a2a2a', tickfont=dict(size=9)),
    yaxis=dict(gridcolor='#0f0f0f', linecolor='#1c1c1c', tickcolor='#2a2a2a', tickfont=dict(size=9)),
    legend=dict(bgcolor='#050505', bordercolor='#1c1c1c', borderwidth=1, font=dict(size=9, color='#555')),
    title_font=dict(size=9, color='#333'),
)

# ─── API ─────────────────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)
MODEL  = "llama-3.3-70b-versatile"

def call_ai(prompt, system="", max_tokens=2048):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=max_tokens).choices[0].message.content

# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
@st.cache_data
def process(raw):
    df = raw.copy()
    df['Full_Name'] = df['First_Name'].str.strip() + " " + df['Last_Name'].str.strip()

    # --- FIX STARTS HERE ---
    # This new block robustly handles any errors in the Attendance_Rate column.
    if 'Attendance_Rate' in df.columns:
        # 1. Convert the column to string, remove the '%' sign and any extra whitespace.
        # 2. Use pd.to_numeric with errors='coerce'. This turns any value that can't be converted
        #    (like an empty cell or text) into a blank value (NaN) instead of crashing.
        # 3. Use .fillna(0.0) to replace any of those blank values with 0.
        cleaned_att = pd.to_numeric(
            df['Attendance_Rate'].astype(str).str.replace('%', '', regex=False).str.strip(),
            errors='coerce'
        ).fillna(0.0)

        # 4. Normalize the data (e.g., convert 95 to 0.95)
        if not cleaned_att.empty and cleaned_att.max() > 1:
            df['Att'] = cleaned_att / 100
        else:
            df['Att'] = cleaned_att
    else:
        # If the column doesn't exist at all, create a default to prevent errors later.
        df['Att'] = 0.5
    # --- FIX ENDS HERE ---

    if 'Role' not in df.columns:
        t = df['Att'].quantile(0.80)
        df['Role'] = df['Att'].apply(lambda x: 'INTERN-MGR' if x >= t else 'VOLUNTEER')
    else:
        df['Role'] = df['Role'].replace({'Intern-Manager': 'INTERN-MGR', 'Volunteer': 'VOLUNTEER'})

    if 'Neighborhood' not in df.columns:
        df['Neighborhood'] = [MOCK_AREAS[i % len(MOCK_AREAS)] for i in range(len(df))]
    return df

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;letter-spacing:5px;color:#e0e0e0;text-transform:uppercase;">NGO OPS</div>
        <div style="font-size:9px;letter-spacing:3px;color:#222;text-transform:uppercase;margin-top:3px;">Command Center</div>
    </div>
    """, unsafe_allow_html=True)
    page = st.radio("Navigation", [
        "Executive Dashboard",
        "Regional Dispatch",
        "Unit Logistics",
        "Growth Auditor",
        "Database Copilot",
    ])
    st.markdown("<hr>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Volunteer Database", type="csv")
    if uploaded_file:
        st.markdown('<div style="font-size:9px;color:#333;letter-spacing:2px;margin-top:8px;">◎ DATABASE ACTIVE</div>', unsafe_allow_html=True)
    st.markdown("""<hr>
    <div style="font-size:9px;color:#1c1c1c;letter-spacing:1px;line-height:2;">
    REQUIRED COLUMNS<br>
    Volunteer_ID · First_Name<br>Last_Name · Phone_Number<br>
    Email · Skills · Interests<br>Has_Vehicle · Attendance_Rate<br>Preferred_Days<br><br>
    OPTIONAL<br>Role · Neighborhood
    </div>""", unsafe_allow_html=True)

# ─── LANDING PAGE ────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="mono-title">NGO Operations Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-sub">Upload your volunteer database via the sidebar to activate all modules.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, (num, name, desc) in zip(cols, [
        ("01", "Executive Dashboard",  "KPIs · Regional density · Skill inventory · Attendance distribution"),
        ("02", "Regional Dispatch",    "Geofenced recruit · Safety buffer · Broadcast generator · Live map"),
        ("03", "Unit Logistics",       "Squad structure · 1:10 ratio · Shift schedule · Field playbook"),
        ("04", "Growth Auditor",       "Skill gaps · Churn predictor · Promotion pipeline"),
        ("05", "Database Copilot",     "Strategic Q&A · AI Ops Director · Donor impact report"),
    ]):
        with col:
            st.markdown(f"""
            <div style="background:#0a0a0a;border:1px solid #1c1c1c;padding:20px 14px;min-height:180px;">
                <div style="font-size:9px;letter-spacing:3px;color:#222;margin-bottom:10px;">{num}</div>
                <div style="font-size:11px;font-weight:700;color:#aaa;letter-spacing:1px;margin-bottom:10px;text-transform:uppercase;">{name}</div>
                <div style="font-size:10px;color:#333;line-height:1.7;">{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.stop()

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
df            = process(pd.read_csv(uploaded_file))
interns_df    = df[df['Role'] == 'INTERN-MGR']
volunteers_df = df[df['Role'] == 'VOLUNTEER']
avg_att       = df['Att'].mean()
neighborhoods = sorted(df['Neighborhood'].unique().tolist())

# ════════════════════════════════════════════════════════════════════════════
#  01 · EXECUTIVE DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "Executive Dashboard":
    st.markdown('<div class="mono-title">Executive Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mono-sub">{len(df)} personnel · {len(neighborhoods)} regions · last updated on upload</div>', unsafe_allow_html=True)

    # KPI row
    k = st.columns(5)
    kpi_data = [
        (len(df),              "Total Workforce",  f"{len(interns_df)} interns / {len(volunteers_df)} vols"),
        (len(interns_df),      "Intern-Managers",  "Leadership tier"),
        (f"{avg_att:.0%}",     "Avg Attendance",   "Operational readiness"),
        (len(neighborhoods),   "Regions Active",   "Neighborhood coverage"),
        (len(df[df['Att']<.5]),"At Risk",          "Attendance below 50%"),
    ]
    for col, (val, lbl, sub) in zip(k, kpi_data):
        with col:
            st.markdown(f'<div class="stat-block"><span class="val">{val}</span><span class="lbl">{lbl}</span><span class="sub">{sub}</span></div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    section("REGIONAL & SKILL INTELLIGENCE")
    c1, c2 = st.columns([3, 2])

    with c1:
        region_data = df.groupby(['Neighborhood','Role']).size().reset_index(name='Count')
        pivot = region_data.pivot(index='Neighborhood', columns='Role', values='Count').fillna(0).reset_index()
        fig = go.Figure()
        if 'INTERN-MGR' in pivot.columns:
            fig.add_bar(name='Intern-Mgr', x=pivot['Neighborhood'], y=pivot['INTERN-MGR'], marker_color='#e0e0e0')
        if 'VOLUNTEER' in pivot.columns:
            fig.add_bar(name='Volunteer',  x=pivot['Neighborhood'], y=pivot['VOLUNTEER'],  marker_color='#2a2a2a')
        fig.update_layout(barmode='stack', title='VOLUNTEER DENSITY BY REGION', **PBASE, height=300)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div style="font-size: 9px; letter-spacing: 3px; color: #2a2a2a; text-transform: uppercase; margin-bottom: 14px;">SKILL INVENTORY — TOP 15</div>', unsafe_allow_html=True)
        sk = pd.Series(parse_skills(df['Skills'])).value_counts().head(15).reset_index()
        sk.columns = ['Skill', 'Count']
        st.dataframe(sk, use_container_width=True, hide_index=True, height=310)

    section("ATTENDANCE & READINESS")
    c3, c4 = st.columns([2, 3])

    with c3:
        bins  = pd.cut(df['Att'], bins=[0,.4,.6,.8,1.01], labels=['<40%','40-60%','60-80%','>80%'])
        bdata = bins.value_counts().sort_index().reset_index()
        bdata.columns = ['Band','Count']
        fig2 = go.Figure(go.Bar(
            x=bdata['Band'], y=bdata['Count'],
            marker_color=['#111','#2a2a2a','#777','#e0e0e0'],
            marker_line_color='#1c1c1c', marker_line_width=1,
            text=bdata['Count'], textposition='outside', textfont=dict(size=9, color='#555'),
        ))
        fig2.update_layout(title='ATTENDANCE DISTRIBUTION', **PBASE, height=280)
        st.plotly_chart(fig2, use_container_width=True)

    with c4:
        readiness = df.groupby('Neighborhood').agg(
            Headcount=('Volunteer_ID','count'),
            Interns=('Role', lambda x: (x=='INTERN-MGR').sum()),
            Volunteers=('Role', lambda x: (x=='VOLUNTEER').sum()),
            Avg_Att=('Att', lambda x: f"{x.mean():.0%}"),
            At_Risk=('Att', lambda x: (x<.5).sum()),
        ).reset_index()
        readiness.columns = ['Region','Headcount','IMs','Volunteers','Avg Att.','At Risk']
        st.dataframe(readiness, use_container_width=True, hide_index=True, height=300)

# ════════════════════════════════════════════════════════════════════════════
#  02 · REGIONAL DISPATCH
# ════════════════════════════════════════════════════════════════════════════
elif page == "Regional Dispatch":
    st.markdown('<div class="mono-title">Regional Dispatch Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-sub">Geofenced recruitment · Safety buffer · AI deployment plan · Live map</div>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        section("EVENT PARAMETERS")
        sel_nbhd     = st.selectbox("Target Neighborhood", ["All Regions"] + neighborhoods)
        event_name   = st.text_input("Event Name",   "Medical Camp")
        event_date   = st.text_input("Date & Time",  "Saturday, 10 AM – 4 PM")
        target_count = st.number_input("Volunteers Needed (Hard Target)", min_value=1, value=10, step=1)
        req_skills   = st.text_input("Required Skills", "First Aid, CPR")
        req_vehicle  = st.checkbox("Vehicle Required")

        local_pool    = volunteers_df if sel_nbhd == "All Regions" else volunteers_df[volunteers_df['Neighborhood'] == sel_nbhd].copy()
        local_avg     = local_pool['Att'].mean() if len(local_pool) > 0 else 0.60
        buffer_target = int(target_count / local_avg) + 1 if local_avg > 0 else target_count * 2

        section("SAFETY BUFFER ENGINE")
        b1, b2, b3 = st.columns(3)
        b1.metric("Local Avg Att.", f"{local_avg:.0%}")
        b2.metric("Buffer Target",  buffer_target)
        b3.metric("Pool Size",      len(local_pool))

        formula = f"Formula: {target_count} ÷ {local_avg:.0%} = {buffer_target}"
        if len(local_pool) < buffer_target:
            warn(f"⚠ {formula}. Pool insufficient — cross-region pull needed.")
        else:
            info(f"✓ {formula}. Pool sufficient.")

    with c_right:
        section("VOLUNTEER DISTRIBUTION MAP")
        map_rows = []
        for nbhd in neighborhoods:
            sub   = volunteers_df[volunteers_df['Neighborhood'] == nbhd]
            coord = NBHD_COORDS.get(nbhd)
            if coord:
                is_sel = sel_nbhd == nbhd or sel_nbhd == "All Regions"
                map_rows.append({
                    'Neighborhood': nbhd, 'lat': coord[0], 'lon': coord[1],
                    'Count': len(sub),
                    'Avg Att': f"{sub['Att'].mean():.0%}" if len(sub) > 0 else 'N/A',
                    'Status': 'Active' if is_sel else 'Inactive',
                })
        mdf = pd.DataFrame(map_rows)
        if len(mdf) > 0:
            fig_map = px.scatter_mapbox(
                mdf, lat='lat', lon='lon', size='Count', color='Status',
                hover_name='Neighborhood',
                hover_data={'lat':False,'lon':False,'Count':True,'Avg Att':True,'Status':False},
                color_discrete_map={'Active':'#e0e0e0','Inactive':'#222'},
                size_max=38, zoom=10,
                center=dict(lat=28.635, lon=77.135),
                mapbox_style='carto-darkmatter',
            )
            fig_map.update_layout(
                paper_bgcolor='#050505', font=dict(family='Space Mono', color='#888', size=10),
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(bgcolor='#050505', bordercolor='#1c1c1c', borderwidth=1,
                            font=dict(size=9, color='#555'), title_text=''),
                height=300,
            )
            st.plotly_chart(fig_map, use_container_width=True)

        section(f"LOCAL ROSTER — {sel_nbhd.upper()}")
        st.dataframe(
            local_pool[['Volunteer_ID','Full_Name','Skills','Has_Vehicle','Attendance_Rate','Preferred_Days']],
            use_container_width=True, hide_index=True, height=200
        )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("Run Dispatch Agent", type="primary"):
        with st.spinner("Analyzing pool · building deployment plan..."):
            safe = local_pool[['Volunteer_ID','Skills','Has_Vehicle','Attendance_Rate','Preferred_Days','Neighborhood']].copy()
            ai_out = call_ai(f"""
EVENT: {event_name} | DATE: {event_date} | REGION: {sel_nbhd}
HARD TARGET: {target_count} | BUFFER TARGET: {buffer_target} (local avg {local_avg:.0%})
REQUIRED SKILLS: {req_skills} | VEHICLE: {req_vehicle}

POOL (no PII):
{safe.to_csv(index=False)}

OUTPUT — use these exact section headers:

## DEPLOYMENT MANIFEST
List exactly {buffer_target} Volunteer IDs (V-XXX). Brief rationale (2 sentences).

## ROLE ASSIGNMENT
Markdown table: Volunteer_ID | Role | Reason

## WHATSAPP BROADCAST
Ready-to-send. Max 160 words. Include: event, date, role, report time, what to bring.

## RISK FLAGS
Gaps, insufficient pool warnings, cross-region pull recommendations.
""", "You are an NGO Dispatch Agent. Be precise, structured, and operational.")

        st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)

        section("CONTACT LIST — PII UNLOCKED (client-side only)")
        found = list(set(re.findall(r'V-\d{3}', ai_out)))
        if found:
            contacts = df[df['Volunteer_ID'].isin(found)][
                ['Volunteer_ID','Full_Name','Phone_Number','Email','Skills','Has_Vehicle','Neighborhood']
            ].copy()
            st.data_editor(contacts, use_container_width=True, hide_index=True)
            info(f"✓ {len(contacts)} contacts. Phone/Email withheld from AI — displayed here only.")

# ════════════════════════════════════════════════════════════════════════════
#  03 · UNIT LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Unit Logistics":
    st.markdown('<div class="mono-title">Unit Logistics & Shift Architect</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-sub">Squad structuring · 1:10 intern ratio · Shift scheduling · Field playbooks</div>', unsafe_allow_html=True)

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        section("EVENT CONFIGURATION")
        event_name   = st.text_input("Event Name",   "Annual Food Drive")
        event_dur    = st.selectbox("Duration",       ["4 hours","6 hours","8 hours","Full Day"])
        shift_size   = st.selectbox("Shift Blocks",   ["2 hours","4 hours","6 hours"])
        nbhd_filter  = st.selectbox("Region Filter",  ["All Regions"] + neighborhoods)
        max_slots    = st.number_input("Volunteer Slots", min_value=5, value=30, step=5)
        roles_needed = st.multiselect("Event Roles", [
            "General Labor","Drivers","Medics","Food Handlers",
            "Coordinators","Registration","Security","Media",
        ], default=["General Labor","Drivers","Coordinators"])

    with c_right:
        section("WORKFORCE PREVIEW")
        filtered = df.copy() if nbhd_filter == "All Regions" else df[df['Neighborhood'] == nbhd_filter].copy()
        n_im  = len(filtered[filtered['Role']=='INTERN-MGR'])
        n_vol = len(filtered[filtered['Role']=='VOLUNTEER'])
        n_sq  = max(n_vol//10, 1)

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Interns",    n_im)
        p2.metric("Volunteers", n_vol)
        p3.metric("Squads",     n_sq,  help="1 IM per 10 Volunteers")
        p4.metric("IM Ratio",   f"1:{n_vol//max(n_im,1)}")

        st.dataframe(
            filtered[['Volunteer_ID','Full_Name','Role','Skills','Preferred_Days','Attendance_Rate']],
            use_container_width=True, hide_index=True, height=240
        )

        section("SQUAD CAPACITY BREAKDOWN")
        sq_names = [f"Squad {chr(65+i)}" for i in range(min(n_sq, 8))]
        fig_sq = go.Figure()
        fig_sq.add_bar(name='Volunteers', x=sq_names, y=[10]*len(sq_names), marker_color='#2a2a2a',
                       marker_line_color='#444', marker_line_width=1)
        fig_sq.add_bar(name='IM Lead',    x=sq_names, y=[1]*len(sq_names),  marker_color='#e0e0e0',
                       marker_line_color='#444', marker_line_width=1)
        fig_sq.update_layout(barmode='stack', title='SQUAD STRUCTURE (1 IM : 10 VOL)',
                             **PBASE, height=200)
        st.plotly_chart(fig_sq, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("Generate Unit Structure & Shift Schedule", type="primary"):
        with st.spinner("Architecting squads · scheduling shifts..."):
            pool_top  = filtered.nlargest(int(max_slots), 'Att')
            safe_pool = pool_top[['Volunteer_ID','Role','Skills','Preferred_Days','Att']].copy()
            ai_out = call_ai(f"""
EVENT: {event_name} | DURATION: {event_dur} | SHIFT BLOCKS: {shift_size}
ROLES: {', '.join(roles_needed)}
RULE: 1 INTERN-MGR lead per 10 VOLUNTEER members.

POOL:
{safe_pool.to_csv(index=False)}

OUTPUT — use these exact section headers:

## SQUAD STRUCTURE
Table: Squad Name | Lead ID | Member IDs | Role

## SHIFT SCHEDULE
Table: Block | Time | Squad | Role | Notes

## FIELD PLAYBOOK
For each role ({', '.join(roles_needed)}): 3-4 bullets. Direct operational language.

## DEPLOYMENT SUMMARY
One paragraph: squads formed, people deployed, shifts covered, IM coverage.
""", "You are an NGO Logistics Architect. Be structured and field-ready.")

        st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)

        section("ROSTER WITH CONTACTS")
        found = list(set(re.findall(r'V-\d{3}', ai_out)))
        if found:
            roster = df[df['Volunteer_ID'].isin(found)][
                ['Volunteer_ID','Full_Name','Role','Phone_Number','Skills','Neighborhood']
            ].copy()
            st.data_editor(roster, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
#  04 · GROWTH AUDITOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "Growth Auditor":
    st.markdown('<div class="mono-title">Growth & Gap Auditor</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-sub">Regional gaps · Churn prediction · Promotion pipeline</div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["  REGIONAL GAPS  ", "  CHURN PREDICTOR  ", "  PROMOTION PIPELINE  "])

    with t1:
        section("SKILL GAP MATRIX")
        g_skills = list(set(parse_skills(df['Skills'])))
        gap_rows = []
        for reg in neighborhoods:
            rdf     = df[df['Neighborhood'] == reg]
            r_sk    = list(set(parse_skills(rdf['Skills'])))
            missing = [s for s in g_skills if s not in r_sk]
            gap_rows.append({'Region':reg,'Headcount':len(rdf),
                             'Skills OK':len(r_sk),'Gaps':len(missing),
                             'Missing': ', '.join(missing[:5])+('…' if len(missing)>5 else '')})
        gap_df = pd.DataFrame(gap_rows).sort_values('Gaps', ascending=False)

        g1, g2 = st.columns([2, 3])
        with g1:
            fig_g = go.Figure(go.Bar(
                x=gap_df['Gaps'], y=gap_df['Region'], orientation='h',
                marker_color='#e0e0e0',
                text=gap_df['Gaps'], textposition='outside', textfont=dict(size=9,color='#555'),
            ))
            fig_g.update_layout(title='GAPS BY REGION', **PBASE, height=320)
            st.plotly_chart(fig_g, use_container_width=True)
        with g2:
            st.dataframe(gap_df, use_container_width=True, hide_index=True, height=340)

        section("GENERATE RECRUITMENT CAMPAIGN")
        sel_reg = st.selectbox("Target Region", neighborhoods, key="gap_reg")
        if st.button("Generate Recruitment Ad", type="primary", key="gap_btn"):
            row = gap_df[gap_df['Region']==sel_reg].iloc[0]
            with st.spinner("Building campaign..."):
                ai_out = call_ai(f"""
Region: {sel_reg} | Headcount: {row['Headcount']} | Missing Skills: {row['Missing']}

## WHATSAPP POST
Community-focused, energetic. Skills needed: {row['Missing']}. 120 words max. Include CTA.

## SOCIAL CAPTION
Professional. 80 words max. Hashtags at end.

## OUTREACH CHANNELS
3 specific, actionable channels to reach people with these skills in {sel_reg}.
""", "You are an NGO talent acquisition specialist.")
            st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)

    with t2:
        section("AT-RISK VOLUNTEER DETECTOR")
        thresh = st.slider("At-Risk Threshold (%)", 30, 70, 50, 5)
        churn  = df[df['Att'] < thresh/100].sort_values('Att')

        cc1, cc2 = st.columns([1, 3])
        with cc1:
            st.markdown(f"""
            <div class="stat-block"><span class="val">{len(churn)}</span>
            <span class="lbl">At-Risk</span><span class="sub">{len(churn)/len(df):.0%} of workforce</span></div>
            """, unsafe_allow_html=True)
            
            fig_c = go.Figure(go.Histogram(x=churn['Att'], nbinsx=8, marker_color='#2a2a2a'))
            fig_c.update_layout(title='AT-RISK ATT. DIST.', **PBASE, height=200, margin=dict(l=0,r=0,t=28,b=0))
            fig_c.update_xaxes(tickformat='.0%')
            st.plotly_chart(fig_c, use_container_width=True)

            churn_by_region = churn.groupby('Neighborhood').size().reset_index(name='Count')
            fig_cr = go.Figure(go.Bar(x=churn_by_region['Count'], y=churn_by_region['Neighborhood'], orientation='h', marker_color='#333'))
            fig_cr.update_layout(title='BY REGION', **PBASE, height=200, margin=dict(l=0,r=0,t=28,b=0))
            st.plotly_chart(fig_cr, use_container_width=True)

        with cc2:
            st.dataframe(
                churn[['Volunteer_ID','Full_Name','Neighborhood','Role','Attendance_Rate','Skills']],
                use_container_width=True, hide_index=True, height=420
            )

        if len(churn) > 0:
            if st.button("Generate Re-activation Campaign", type="primary", key="churn_btn"):
                with st.spinner("Building re-engagement strategy..."):
                    safe_c = churn[['Volunteer_ID','Neighborhood','Skills','Attendance_Rate']].head(20)
                    ai_out = call_ai(f"""
{len(churn)} at-risk volunteers (attendance < {thresh}%).

Sample profiles:
{safe_c.to_csv(index=False)}

## RE-ENGAGEMENT MESSAGE
Warm, non-judgmental WhatsApp. Acknowledge absence, celebrate past work, invite return. 150 words max.

## RE-ACTIVATION STRATEGY
3 tactical approaches (micro-events, personal outreach, recognition programs).
""", "You are an NGO community engagement manager.")
                st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)

    with t3:
        section("PROMOTION PIPELINE")
        p_thresh   = st.slider("Promotion Threshold (%)", 70, 95, 82, 1)
        candidates = df[(df['Att'] >= p_thresh/100) & (df['Role']=='VOLUNTEER')].sort_values('Att', ascending=False)

        pp1, pp2 = st.columns([1, 2])
        with pp1:
            st.markdown(f"""
            <div class="stat-block"><span class="val">{len(candidates)}</span>
            <span class="lbl">Candidates</span><span class="sub">Att ≥ {p_thresh}%</span></div>
            <div class="stat-block" style="margin-top:1px;"><span class="val">1:{len(volunteers_df)//max(len(interns_df),1)}</span>
            <span class="lbl">Current IM Ratio</span><span class="sub">Target: 1:10</span></div>
            """, unsafe_allow_html=True)

            top10 = candidates.head(10)
            fig_p = go.Figure(go.Bar(
                x=top10['Volunteer_ID'], y=top10['Att'],
                marker_color='#e0e0e0',
                text=[f"{v:.0%}" for v in top10['Att']],
                textposition='outside', textfont=dict(size=8,color='#555'),
            ))
            fig_p.update_layout(title='TOP CANDIDATE SCORES', **PBASE, height=220)
            fig_p.update_yaxes(tickformat='.0%')
            fig_p.update_xaxes(tickangle=-40)
            st.plotly_chart(fig_p, use_container_width=True)

        with pp2:
            st.dataframe(
                candidates[['Volunteer_ID','Full_Name','Neighborhood','Attendance_Rate','Skills']],
                use_container_width=True, hide_index=True, height=380
            )

        if len(candidates) > 0:
            if st.button("Generate Promotion Briefing", type="primary", key="promo_btn"):
                with st.spinner("Building promotion assessment..."):
                    safe_p = candidates[['Volunteer_ID','Neighborhood','Skills','Attendance_Rate']].head(10)
                    ai_out = call_ai(f"""
Candidates (att ≥ {p_thresh}%):
{safe_p.to_csv(index=False)}

Current: {len(interns_df)} IMs, {len(volunteers_df)} Volunteers. Target ratio: 1:10.

## TOP 3 CANDIDATES
ID, reason for selection, what they bring to leadership.

## INTERN-MANAGER ROLE DEFINITION
Responsibilities, authority, what they own in the field.

## ONBOARDING CHECKLIST
7 concrete steps within 2 weeks.

## CONGRATULATORY MESSAGE TEMPLATE
Warm message to send each selected candidate.
""", "You are an NGO HR strategist.")
                st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
#  05 · DATABASE COPILOT
# ════════════════════════════════════════════════════════════════════════════
elif page == "Database Copilot":
    st.markdown('<div class="mono-title">Database Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="mono-sub">AI Ops Director · Strategic workforce intelligence · No PII exposure</div>', unsafe_allow_html=True)

    region_ctx = df.groupby('Neighborhood').agg(
        Headcount=('Volunteer_ID','count'),
        IMs=('Role', lambda x: (x=='INTERN-MGR').sum()),
        Vols=('Role', lambda x: (x=='VOLUNTEER').sum()),
        Avg_Att=('Att','mean'),
    ).reset_index().to_csv(index=False)

    top_skills = pd.Series(parse_skills(df['Skills'])).value_counts().head(20).to_string()

    SYSTEM = f"""You are the NGO Operations Director AI — a strategic advisor.

SNAPSHOT:
- Total: {len(df)} ({len(interns_df)} Intern-Managers, {len(volunteers_df)} Volunteers)
- Avg Attendance: {avg_att:.0%} | Regions: {len(neighborhoods)} | At-Risk (<50%): {len(df[df['Att']<0.50])}
- Promotion Candidates (>82%, Volunteer): {len(df[(df['Att']>=0.82)&(df['Role']=='VOLUNTEER')])}

REGIONAL DATA:
{region_ctx}

TOP SKILLS:
{top_skills}

Answer STRATEGIC questions about workforce density, coverage, event capacity, skill gaps, deployment limits, ratio analysis. Cite real numbers. Never reveal individual PII."""

    if "cop_msgs" not in st.session_state:
        st.session_state.cop_msgs = []

    section("QUICK QUERIES")
    qcols = st.columns(4)
    quick_queries = [
        "Which region has weakest coverage?",
        "Can we run 3 simultaneous events?",
        "Which skills are critically understaffed?",
        "What is our max deployment capacity?",
    ]
    for qcol, q in zip(qcols, quick_queries):
        if qcol.button(q, key=f"q_{q[:10]}"):
            st.session_state.cop_msgs.append({"role":"user","content":q})
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":SYSTEM}] + st.session_state.cop_msgs,
                max_tokens=1024
            )
            ai = r.choices[0].message.content
            st.session_state.cop_msgs.append({"role":"assistant","content":ai})
            st.rerun()

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    for msg in st.session_state.cop_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your Ops Director..."):
        st.session_state.cop_msgs.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            msgs = [{"role":"system","content":SYSTEM}] + st.session_state.cop_msgs
            r    = client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=1024)
            ai   = r.choices[0].message.content
            st.markdown(ai)
            st.session_state.cop_msgs.append({"role":"assistant","content":ai})

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns([1,1,2])

    if d1.button("Clear Chat", key="clear_cop"):
        st.session_state.cop_msgs = []
        st.rerun()

    if d2.button("Generate Donor Impact Report", type="primary", key="donor_rpt"):
        with st.spinner("Compiling report..."):
            ai_out = call_ai(f"""
Write a professional donor-ready NGO Workforce Impact Report.

DATA:
- Workforce: {len(df)} across {len(neighborhoods)} neighborhoods
- Intern-Managers: {len(interns_df)} | Volunteers: {len(volunteers_df)}
- Avg Attendance: {avg_att:.0%}
- At-Risk: {len(df[df['Att']<0.5])} flagged for re-engagement
- Top Skills: {', '.join(pd.Series(parse_skills(df['Skills'])).value_counts().head(8).index.tolist())}

REGIONAL:
{region_ctx}

Sections:
1. EXECUTIVE SUMMARY — 3 sentences, no bullets. Inspiring and factual.
2. WORKFORCE STRENGTH — Key numbers.
3. REGIONAL REACH — Top 3 regions.
4. OPERATIONAL CAPACITY — Events possible, max deployment.
5. GROWTH TRAJECTORY — 1 forward-looking paragraph.
""", "You are a senior NGO communications strategist.")
        section("DONOR IMPACT REPORT")
        st.markdown(f'<div class="ai-block">{ai_out}</div>', unsafe_allow_html=True)