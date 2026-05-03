import streamlit as st
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="NGO Operations Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLING ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] * { color: #c8d8e8 !important; }
    section[data-testid="stSidebar"] .stRadio > label {
        font-family: 'Space Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 2px !important;
        color: #4a7fa5 !important;
        text-transform: uppercase;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        font-size: 14px !important;
        letter-spacing: 0 !important;
        text-transform: none !important;
        color: #c8d8e8 !important;
        padding: 8px 4px;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
        color: #4fc3f7 !important;
        font-weight: 600 !important;
    }

    /* Main background */
    .main .block-container {
        background-color: #060e1a;
        padding-top: 1.5rem;
    }
    .stApp { background-color: #060e1a; }

    /* Page title bar */
    .page-header {
        background: linear-gradient(90deg, #0d1f3c 0%, #112240 100%);
        border-left: 4px solid #4fc3f7;
        border-bottom: 1px solid #1e3a5f;
        padding: 16px 24px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 24px;
    }
    .page-header h2 { margin: 0; color: #e8f4fd; font-size: 1.4em; font-weight: 600; }
    .page-header p { margin: 4px 0 0 0; color: #5a8ab0; font-size: 0.85em; }

    /* KPI Cards */
    .kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px;
        background: linear-gradient(135deg, #0d1f3c 0%, #112240 100%);
        border: 1px solid #1e3a5f;
        border-top: 3px solid #4fc3f7;
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
    }
    .kpi-number {
        font-family: 'Space Mono', monospace;
        font-size: 2em; font-weight: 700;
        color: #4fc3f7; display: block; line-height: 1;
    }
    .kpi-label { font-size: 0.75em; color: #5a8ab0; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; display: block; }
    .kpi-sub { font-size: 0.7em; color: #3a6080; margin-top: 2px; display: block; }

    /* Section dividers */
    .section-label {
        font-family: 'Space Mono', monospace;
        font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
        color: #2a5070; border-bottom: 1px solid #1e3a5f;
        padding-bottom: 6px; margin: 24px 0 12px 0;
    }

    /* Status badges */
    .badge {
        display: inline-block; padding: 2px 8px; border-radius: 3px;
        font-size: 0.72em; font-weight: 600; font-family: 'Space Mono', monospace;
        letter-spacing: 0.5px;
    }
    .badge-intern { background: #0d2a1a; color: #52d68a; border: 1px solid #2a7a4a; }
    .badge-volunteer { background: #0d1f3a; color: #4fc3f7; border: 1px solid #2a5a8a; }
    .badge-risk { background: #2a0d0d; color: #f77; border: 1px solid #7a2a2a; }
    .badge-promo { background: #2a2a0d; color: #ffd740; border: 1px solid #7a7a0d; }

    /* Alert box */
    .alert-box {
        background: #0d1f0d; border: 1px solid #2a5a2a; border-left: 4px solid #52d68a;
        border-radius: 6px; padding: 12px 16px; margin: 12px 0;
        color: #a0d8a0; font-size: 0.88em;
    }
    .warning-box {
        background: #2a1a0d; border: 1px solid #7a4a0d; border-left: 4px solid #ffa040;
        border-radius: 6px; padding: 12px 16px; margin: 12px 0;
        color: #d4a060; font-size: 0.88em;
    }

    /* Streamlit component overrides */
    div[data-testid="metric-container"] {
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 12px;
    }
    .stTabs [data-baseweb="tab-list"] { background: #0d1f3c; border-radius: 8px 8px 0 0; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: #5a8ab0 !important; font-size: 13px; }
    .stTabs [aria-selected="true"] { color: #4fc3f7 !important; }

    /* Tables */
    .stDataFrame { border: 1px solid #1e3a5f !important; border-radius: 8px; }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #1565c0, #0d47a1) !important;
        border: 1px solid #4fc3f7 !important;
        color: #e8f4fd !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #1976d2, #1565c0) !important;
        box-shadow: 0 0 12px rgba(79,195,247,0.3) !important;
    }

    /* Sidebar logo area */
    .sidebar-logo {
        font-family: 'Space Mono', monospace;
        font-size: 18px; font-weight: 700; color: #4fc3f7;
        letter-spacing: 1px; margin-bottom: 4px;
    }
    .sidebar-sub { font-size: 10px; color: #2a5070; letter-spacing: 3px; text-transform: uppercase; }

    /* AI output card */
    .ai-output {
        background: #0a1628;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 20px;
        margin-top: 12px;
        line-height: 1.7;
        color: #c8d8e8;
    }

    div[data-testid="stExpander"] {
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── API & MODEL SETUP ───────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    st.error("⚠️ GROQ_API_KEY not found. Set it in .env or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)
MODEL = "llama-3.3-70b-versatile"

def call_ai(prompt: str, system: str = None, max_tokens: int = 2048) -> str:
    """Single AI call helper with optional system prompt."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    res = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=max_tokens)
    return res.choices[0].message.content

# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
def process_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df['Full_Name'] = df['First_Name'].str.strip() + " " + df['Last_Name'].str.strip()

    # Attendance → float
    if df['Attendance_Rate'].dtype == object:
        df['Attendance_Float'] = (
            df['Attendance_Rate'].astype(str)
            .str.replace('%', '', regex=False)
            .str.strip()
            .astype(float)
        )
        if df['Attendance_Float'].max() > 1:
            df['Attendance_Float'] = df['Attendance_Float'] / 100
    else:
        df['Attendance_Float'] = df['Attendance_Rate'].astype(float)
        if df['Attendance_Float'].max() > 1:
            df['Attendance_Float'] = df['Attendance_Float'] / 100

    # Workforce tier: use 'Role' column if present, else derive from top 20% attendance
    if 'Role' not in df.columns:
        threshold = df['Attendance_Float'].quantile(0.80)
        df['Role'] = df['Attendance_Float'].apply(
            lambda x: 'Intern-Manager' if x >= threshold else 'Volunteer'
        )

    # Neighborhood: use column if present, else cycle through mock ones deterministically
    if 'Neighborhood' not in df.columns:
        mock_areas = [
            'Paschim Vihar', 'Rohini', 'Dwarka', 'Janakpuri', 'Pitampura',
            'Saket', 'Lajpat Nagar', 'Karol Bagh', 'Vasant Kunj', 'Connaught Place'
        ]
        df['Neighborhood'] = [mock_areas[i % len(mock_areas)] for i in range(len(df))]

    return df

def parse_skills(series: pd.Series) -> list[str]:
    skills = []
    for val in series.dropna():
        skills.extend([s.strip() for s in str(val).split(';') if s.strip()])
    return skills

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🎯 NGO OPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Command Center</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "📊  Executive Dashboard",
            "🗺️  Regional Dispatch Agent",
            "🏗️  Unit Logistics & Shifts",
            "📈  Growth & Gap Auditor",
            "🧠  Database Copilot",
        ],
    )
    st.markdown("---")
    uploaded_file = st.file_uploader("📁 Volunteer Database (CSV)", type="csv")

    if uploaded_file:
        st.markdown('<div class="alert-box">✅ Database loaded</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:10px;color:#2a5070;letter-spacing:1px;">EXPECTED COLUMNS<br>Volunteer_ID · First_Name · Last_Name<br>Phone_Number · Email · Interests<br>Skills · Has_Vehicle · Attendance_Rate<br>Preferred_Days<br><br>Optional: Role · Neighborhood</p>', unsafe_allow_html=True)

# ─── NO FILE UPLOADED ────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px;">
        <div style="font-family:'Space Mono',monospace; font-size:48px; color:#4fc3f7; margin-bottom:8px;">🎯</div>
        <h1 style="color:#e8f4fd; font-size:2.2em; margin:0;">NGO Operations Command Center</h1>
        <p style="color:#5a8ab0; font-size:1.1em; margin:12px 0 40px 0;">Upload your volunteer database to activate all command modules.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    modules = [
        ("📊", "Executive Dashboard", "Live KPIs, regional density maps, and skill inventory at a glance."),
        ("🗺️", "Regional Dispatch", "Geofenced recruitment with AI safety-buffer calculations."),
        ("🏗️", "Unit Logistics", "Auto-structure squads, assign intern leads, generate shift schedules."),
        ("📈", "Growth Auditor", "Gap analysis, churn prediction, and promotion pipeline."),
        ("🧠", "Database Copilot", "Strategic Q&A with your AI Ops Director.")
    ]
    for col, (icon, name, desc) in zip([c1, c2, c3, c4, c5], modules):
        with col:
            st.markdown(f"""
            <div style="background:#0d1f3c;border:1px solid #1e3a5f;border-top:3px solid #4fc3f7;
                        border-radius:10px;padding:20px 14px;text-align:center;min-height:160px;">
                <div style="font-size:2em">{icon}</div>
                <div style="color:#4fc3f7;font-weight:600;font-size:0.9em;margin:8px 0 6px;">{name}</div>
                <div style="color:#5a8ab0;font-size:0.78em;line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
df = process_dataframe(pd.read_csv(uploaded_file))
interns_df   = df[df['Role'] == 'Intern-Manager']
volunteers_df = df[df['Role'] == 'Volunteer']
avg_attendance = df['Attendance_Float'].mean()
neighborhoods  = sorted(df['Neighborhood'].unique().tolist())

# ════════════════════════════════════════════════════════════════════════════
# PAGE ① — EXECUTIVE DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "📊  Executive Dashboard":
    st.markdown("""
    <div class="page-header">
        <h2>📊 Executive Dashboard</h2>
        <p>Live workforce overview · Regional density · Skill inventory</p>
    </div>
    """, unsafe_allow_html=True)

    # — KPI Row —
    k1, k2, k3, k4, k5 = st.columns(5)
    ratio = f"1 : {len(volunteers_df) // max(len(interns_df), 1)}"
    churn_count = len(df[df['Attendance_Float'] < 0.50])

    k1.metric("Total Workforce",   len(df))
    k2.metric("Intern-Managers",   len(interns_df),   delta="Leadership tier")
    k3.metric("Field Volunteers",  len(volunteers_df))
    k4.metric("Avg Attendance",    f"{avg_attendance:.0%}", delta="Operational readiness")
    k5.metric("At-Risk (< 50%)",   churn_count,       delta_color="inverse")

    st.markdown('<div class="section-label">Regional & Skill Intelligence</div>', unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Regional Volunteer Density")
        region_summary = (
            df.groupby(['Neighborhood', 'Role'])
            .size()
            .reset_index(name='Count')
        )

        try:
            import plotly.express as px
            fig = px.bar(
                region_summary, x='Neighborhood', y='Count', color='Role',
                color_discrete_map={'Intern-Manager': '#52d68a', 'Volunteer': '#4fc3f7'},
                template='plotly_dark', barmode='stack'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                margin=dict(l=0, r=0, t=30, b=0),
                font=dict(color='#c8d8e8')
            )
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pivot = region_summary.pivot(index='Neighborhood', columns='Role', values='Count').fillna(0)
            st.bar_chart(pivot)

        # Attendance distribution
        st.subheader("Attendance Distribution by Tier")
        att_bins = pd.cut(df['Attendance_Float'], bins=[0, 0.5, 0.7, 0.85, 1.01],
                          labels=['<50% (At-Risk)', '50–70%', '70–85%', '>85% (Elite)'])
        att_summary = att_bins.value_counts().sort_index().reset_index()
        att_summary.columns = ['Band', 'Count']
        try:
            fig2 = px.bar(att_summary, x='Band', y='Count', template='plotly_dark',
                          color='Count', color_continuous_scale='blues')
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                               margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        except ImportError:
            st.bar_chart(att_summary.set_index('Band'))

    with right:
        st.subheader("Skill Inventory")
        all_skills = parse_skills(df['Skills'])
        skill_counts = pd.Series(all_skills).value_counts().head(15).reset_index()
        skill_counts.columns = ['Skill', 'Count']
        st.dataframe(skill_counts, use_container_width=True, hide_index=True, height=240)

        st.subheader("Regional Readiness")
        readiness = (
            df.groupby('Neighborhood')
            .agg(
                Headcount=('Volunteer_ID', 'count'),
                Avg_Att=('Attendance_Float', lambda x: f"{x.mean():.0%}"),
                Interns=('Role', lambda x: (x == 'Intern-Manager').sum())
            )
            .reset_index()
            .rename(columns={'Avg_Att': 'Avg Att.', 'Interns': 'IM'})
        )
        st.dataframe(readiness, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE ② — REGIONAL DISPATCH AGENT
# ════════════════════════════════════════════════════════════════════════════
elif page == "🗺️  Regional Dispatch Agent":
    st.markdown("""
    <div class="page-header">
        <h2>🗺️ Regional Dispatch Agent</h2>
        <p>Geofenced recruitment · AI safety-buffer calculation · Broadcast generator</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 2])

    with left:
        st.markdown('<div class="section-label">Event Parameters</div>', unsafe_allow_html=True)
        selected_neighborhood = st.selectbox("📍 Target Neighborhood", ["All Regions"] + neighborhoods)
        event_name   = st.text_input("Event Name", "Medical Camp – Paschim Vihar")
        event_date   = st.text_input("Date & Time", "Saturday, 10 AM – 4 PM")
        target_count = st.number_input("Volunteers Needed (Hard Target)", min_value=1, value=10, step=1)
        req_skills   = st.text_input("Required Skills (comma-separated)", "First Aid, CPR")
        req_vehicle  = st.checkbox("Must Have Vehicle 🚗")

        # — Safety Buffer Engine —
        if selected_neighborhood == "All Regions":
            local_pool = volunteers_df.copy()
        else:
            local_pool = volunteers_df[volunteers_df['Neighborhood'] == selected_neighborhood].copy()

        local_avg = local_pool['Attendance_Float'].mean() if len(local_pool) > 0 else 0.60
        buffer_target = int(target_count / local_avg) + 1 if local_avg > 0 else target_count * 2

        st.markdown('<div class="section-label">Safety Buffer Engine</div>', unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        b1.metric("Local Avg Att.", f"{local_avg:.0%}")
        b2.metric("Buffer Target",  buffer_target, help="Auto-calculated: Hard Target ÷ Local Avg Attendance")
        b3.metric("Local Pool",     len(local_pool))

        if len(local_pool) < buffer_target:
            st.markdown(f'<div class="warning-box">⚠️ Local pool ({len(local_pool)}) is smaller than buffer target ({buffer_target}). Agent will flag for cross-region pull.</div>', unsafe_allow_html=True)

    with right:
        st.markdown(f'<div class="section-label">Local Roster — {selected_neighborhood}</div>', unsafe_allow_html=True)
        display_pool = local_pool[['Volunteer_ID', 'Full_Name', 'Skills', 'Has_Vehicle', 'Attendance_Rate', 'Preferred_Days']].copy()
        st.dataframe(display_pool, use_container_width=True, hide_index=True, height=320)

    st.markdown("---")

    if st.button("🚀 Activate Dispatch Agent", type="primary"):
        with st.spinner("Agent analyzing volunteer pool and generating deployment plan..."):

            # PII-safe data for AI
            safe_df = local_pool[['Volunteer_ID', 'Skills', 'Has_Vehicle', 'Attendance_Rate', 'Preferred_Days', 'Neighborhood']].copy()

            dispatch_prompt = f"""
You are an NGO Regional Dispatch Agent. Build a complete deployment plan.

EVENT: {event_name}
DATE: {event_date}
REGION: {selected_neighborhood}
HARD TARGET: {target_count} volunteers
SAFETY BUFFER TARGET: {buffer_target} (local avg attendance is {local_avg:.0%})
REQUIRED SKILLS: {req_skills}
VEHICLE REQUIRED: {req_vehicle}

AVAILABLE VOLUNTEER POOL (no PII — IDs only):
{safe_df.to_csv(index=False)}

PRODUCE EXACTLY THESE SECTIONS:

## 1. DEPLOYMENT MANIFEST
Select exactly {buffer_target} Volunteer IDs (format: V-XXX). Prioritize: skill match > attendance rate > vehicle (if required). List selected IDs and brief rationale.

## 2. ROLE ASSIGNMENT
Group selected IDs by their function at the event (e.g., Medics, Drivers, Support Staff, Registration). Each person gets one role.

## 3. WHATSAPP BROADCAST MESSAGE
One professional, warm WhatsApp message to send to the full selected group. Include: event name, date, their role, what to bring, and a clear call-to-action. Max 180 words.

## 4. RISK FLAGS
If pool is insufficient or skills are missing, flag clearly and suggest a mitigation (e.g., pull from adjacent region, recruit external).

Format with clear headers. IDs must be in V-XXX format.
"""
            ai_text = call_ai(dispatch_prompt, system="You are a precise NGO Operations Dispatch Agent. Be structured, operational, and concise.")

        st.markdown(f'<div class="ai-output">{ai_text}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Actionable Contact List — PII Revealed (Client-Side Only)</div>', unsafe_allow_html=True)
        found_ids = list(set(re.findall(r'V-\d{3}', ai_text)))
        if found_ids:
            contacts = df[df['Volunteer_ID'].isin(found_ids)][
                ['Volunteer_ID', 'Full_Name', 'Phone_Number', 'Email', 'Skills', 'Has_Vehicle', 'Neighborhood']
            ].copy()
            st.data_editor(contacts, use_container_width=True, hide_index=True)
            st.markdown(f'<div class="alert-box">✅ {len(contacts)} contacts identified. Phone & Email were never sent to the AI — revealed here only.</div>', unsafe_allow_html=True)
        else:
            st.info("No V-XXX IDs found in AI output. Ensure your CSV uses the V-XXX format.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE ③ — UNIT LOGISTICS & SHIFTS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🏗️  Unit Logistics & Shifts":
    st.markdown("""
    <div class="page-header">
        <h2>🏗️ Unit Logistics & Shift Architect</h2>
        <p>Squad structuring · 1:10 intern-to-volunteer ratio · Shift-block scheduling · Field playbooks</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 2])

    with left:
        st.markdown('<div class="section-label">Event Configuration</div>', unsafe_allow_html=True)
        event_name     = st.text_input("Event Name", "Annual Food Drive 2025")
        event_duration = st.selectbox("Event Duration", ["4 hours", "6 hours", "8 hours", "Full Day (10+ hours)"])
        shift_size     = st.selectbox("Shift Block Size", ["2 hours", "4 hours", "6 hours"])
        nbhd_filter    = st.selectbox("Region Filter", ["All Regions"] + neighborhoods)
        max_slots      = st.number_input("Total Volunteer Slots", min_value=5, value=30, step=5)
        roles_needed   = st.multiselect(
            "Roles Required at Event",
            ["General Labor", "Drivers", "Medics", "Food Handlers", "Coordinators", "Registration Desk", "Security", "Media/Documentation"],
            default=["General Labor", "Drivers", "Coordinators"]
        )

    with right:
        st.markdown('<div class="section-label">Workforce Preview</div>', unsafe_allow_html=True)

        if nbhd_filter == "All Regions":
            filtered = df.copy()
        else:
            filtered = df[df['Neighborhood'] == nbhd_filter].copy()

        n_im  = len(filtered[filtered['Role'] == 'Intern-Manager'])
        n_vol = len(filtered[filtered['Role'] == 'Volunteer'])
        squads_possible = max(n_vol // 10, 1)

        p1, p2, p3 = st.columns(3)
        p1.metric("Interns Available",    n_im)
        p2.metric("Volunteers Available", n_vol)
        p3.metric("Squads Possible",      squads_possible, help="1 Intern-Manager per 10 Volunteers")

        preview = filtered[['Volunteer_ID', 'Full_Name', 'Role', 'Skills', 'Preferred_Days', 'Attendance_Rate']].copy()
        st.dataframe(preview, use_container_width=True, hide_index=True, height=280)

    st.markdown("---")

    if st.button("⚙️ Generate Unit Structure & Shift Schedule", type="primary"):
        with st.spinner("Architecting squads, assigning leads, scheduling shifts..."):

            pool_top = filtered.nlargest(int(max_slots), 'Attendance_Float')
            safe_pool = pool_top[['Volunteer_ID', 'Role', 'Skills', 'Preferred_Days', 'Attendance_Float']].copy()

            logistics_prompt = f"""
You are an NGO Logistics Architect. Structure this workforce for a large-scale event.

EVENT: {event_name}
DURATION: {event_duration} | SHIFT BLOCK: {shift_size}
ROLES REQUIRED: {', '.join(roles_needed)}
RULE: Assign exactly 1 Intern-Manager as Squad Lead for every 10 Volunteers.

WORKFORCE POOL:
{safe_pool.to_csv(index=False)}

PRODUCE EXACTLY THESE SECTIONS:

## 1. SQUAD STRUCTURE
Organize into named squads (Squad Alpha, Squad Bravo, etc.)
For each squad: Squad Name | Lead (Intern-Manager ID) | Member IDs | Assigned Role
Present as a markdown table.

## 2. SHIFT SCHEDULE
Break {event_duration} into {shift_size} blocks.
Assign squads to shifts. Present as a clear table:
Shift Block | Time | Squad(s) Assigned | Role

## 3. FIELD PLAYBOOK
Write 3-4 bullet point instructions for each role: {', '.join(roles_needed)}
Tone: direct, operational. No fluff.

## 4. DEPLOYMENT SUMMARY
Total units formed | Total people deployed | Shifts covered | Intern-Manager coverage ratio
"""
            ai_text = call_ai(logistics_prompt, system="You are a precise NGO Logistics Architect. Produce structured, operational field-ready plans.")

        st.markdown(f'<div class="ai-output">{ai_text}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Final Roster with Contacts</div>', unsafe_allow_html=True)
        found_ids = list(set(re.findall(r'V-\d{3}', ai_text)))
        if found_ids:
            roster = df[df['Volunteer_ID'].isin(found_ids)][
                ['Volunteer_ID', 'Full_Name', 'Role', 'Phone_Number', 'Skills', 'Neighborhood']
            ].copy()
            st.data_editor(roster, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE ④ — GROWTH & GAP AUDITOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "📈  Growth & Gap Auditor":
    st.markdown("""
    <div class="page-header">
        <h2>📈 Growth & Gap Auditor</h2>
        <p>Regional skill gaps · Churn prediction · Promotion pipeline · Recruitment campaigns</p>
    </div>
    """, unsafe_allow_html=True)

    audit_tab1, audit_tab2, audit_tab3 = st.tabs([
        "🗺️ Regional Gap Analysis",
        "⚠️ Churn Predictor",
        "🏆 Promotion Pipeline"
    ])

    # ── TAB A: REGIONAL GAP ANALYSIS ──
    with audit_tab1:
        global_skills = list(set(parse_skills(df['Skills'])))

        gap_rows = []
        for region in neighborhoods:
            rdf = df[df['Neighborhood'] == region]
            r_skills = list(set(parse_skills(rdf['Skills'])))
            missing  = [s for s in global_skills if s not in r_skills]
            gap_rows.append({
                'Region':         region,
                'Headcount':      len(rdf),
                'Skills Present': len(r_skills),
                'Skills Missing': len(missing),
                'Critical Gaps':  ', '.join(missing[:6]) + ('…' if len(missing) > 6 else '')
            })

        gap_df = pd.DataFrame(gap_rows).sort_values('Skills Missing', ascending=False)
        st.dataframe(gap_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        sel_region = st.selectbox("Generate Recruitment Campaign for:", neighborhoods)

        if st.button("🎯 Generate Targeted Recruitment Ad", type="primary", key="gap_btn"):
            row = gap_df[gap_df['Region'] == sel_region].iloc[0]
            with st.spinner("AI crafting targeted recruitment campaign..."):
                ad_prompt = f"""
Region: {sel_region} | Headcount: {row['Headcount']} | Missing Skills: {row['Critical Gaps']}

Generate:

## 1. WHATSAPP RECRUITMENT POST
Casual, energetic, community-focused. Target people with these skills: {row['Critical Gaps']}. Max 120 words. Include a clear call-to-action.

## 2. SOCIAL MEDIA CAPTION (LinkedIn / Instagram)
Professional tone. Max 100 words. Hashtags at the end.

## 3. OUTREACH STRATEGY
3 specific, actionable channels to reach people with these skills in {sel_region} (e.g., local colleges, clinics, RWA notice boards).
"""
                ad_response = call_ai(ad_prompt, system="You are an NGO talent acquisition specialist. Write compelling, hyper-targeted recruitment content.")
            st.markdown(f'<div class="ai-output">{ad_response}</div>', unsafe_allow_html=True)

    # ── TAB B: CHURN PREDICTOR ──
    with audit_tab2:
        churn_thresh = st.slider("At-Risk Attendance Threshold (%)", 30, 70, 50, 5,
                                 help="Volunteers below this rate are flagged as at-risk.")
        churn = df[df['Attendance_Float'] < (churn_thresh / 100)].sort_values('Attendance_Float')
        churn_display = churn[['Volunteer_ID', 'Full_Name', 'Neighborhood', 'Role', 'Attendance_Rate', 'Skills']].copy()

        c1, c2 = st.columns([1, 3])
        c1.metric("At-Risk Volunteers", len(churn), delta=f"of {len(df)} total", delta_color="inverse")
        c1.metric("% of Workforce",  f"{len(churn)/len(df):.0%}", delta_color="inverse")

        with c2:
            st.dataframe(churn_display, use_container_width=True, hide_index=True, height=200)

        if st.button("📣 Generate Re-activation Campaign", type="primary", key="churn_btn") and len(churn) > 0:
            with st.spinner("Building re-engagement strategy..."):
                churn_safe = churn[['Volunteer_ID', 'Neighborhood', 'Skills', 'Attendance_Rate']].head(20)
                reactivation_prompt = f"""
We have {len(churn)} at-risk volunteers (attendance below {churn_thresh}%).

Sample at-risk profiles:
{churn_safe.to_csv(index=False)}

Produce:

## 1. RE-ENGAGEMENT MESSAGE
Warm, non-judgmental WhatsApp message to send the group. Acknowledge the gap, celebrate past contributions, invite them back. Max 150 words.

## 2. RE-ACTIVATION STRATEGY
3 tactical approaches to bring these volunteers back (e.g., personal check-in calls, low-commitment micro-events, recognition programs).

## 3. INCENTIVE STRUCTURE
Concrete incentives to boost attendance: recognition tiers, certificates, role upgrades, etc.

## 4. 2-WEEK ACTION PLAN
Day-by-day or step-by-step re-activation playbook for the NGO coordinator.

Tone: warm, community-first, not corporate.
"""
                reactivation_response = call_ai(reactivation_prompt, system="You are an NGO community engagement manager. Write in a warm, human, action-oriented style.")
            st.markdown(f'<div class="ai-output">{reactivation_response}</div>', unsafe_allow_html=True)

    # ── TAB C: PROMOTION PIPELINE ──
    with audit_tab3:
        promo_thresh = st.slider("Promotion Threshold (%)", 70, 95, 82, 1,
                                 help="Volunteers at or above this attendance rate are flagged for promotion.")

        candidates = df[
            (df['Attendance_Float'] >= promo_thresh / 100) &
            (df['Role'] == 'Volunteer')
        ].sort_values('Attendance_Float', ascending=False)

        current_ratio = f"1 : {len(volunteers_df) // max(len(interns_df), 1)}"
        ideal_ratio   = "1 : 10"

        p1, p2, p3 = st.columns(3)
        p1.metric("Promotion Candidates", len(candidates))
        p2.metric("Current IM Ratio",     current_ratio, help="Intern-Managers to Volunteers")
        p3.metric("Ideal Ratio",          ideal_ratio)

        promo_display = candidates[['Volunteer_ID', 'Full_Name', 'Neighborhood', 'Attendance_Rate', 'Skills']].copy()
        st.dataframe(promo_display, use_container_width=True, hide_index=True, height=220)

        if st.button("📋 Generate Promotion Briefing", type="primary", key="promo_btn") and len(candidates) > 0:
            with st.spinner("Building promotion assessment and onboarding plan..."):
                promo_safe = candidates[['Volunteer_ID', 'Neighborhood', 'Skills', 'Attendance_Rate']].head(10)
                promo_prompt = f"""
These volunteers have exceptional commitment (attendance ≥ {promo_thresh}%) and are candidates for Intern-Manager promotion.

Candidates:
{promo_safe.to_csv(index=False)}

Current State: {len(interns_df)} Intern-Managers, {len(volunteers_df)} Volunteers (ratio {current_ratio}, target 1:10)

Produce:

## 1. TOP 3 CANDIDATES
Recommend the 3 best candidates with specific reasoning for each.

## 2. INTERN-MANAGER ROLE DEFINITION
What this role means in the field: responsibilities, expectations, authority, and what they own.

## 3. ONBOARDING CHECKLIST
6-8 concrete steps to onboard a new Intern-Manager within 2 weeks.

## 4. CONGRATULATORY MESSAGE TEMPLATE
A message to send to each selected candidate. Warm, proud, specific.

Be concrete and operational.
"""
                promo_response = call_ai(promo_prompt, system="You are an NGO HR strategist. Be specific, structured, and inspiring.")
            st.markdown(f'<div class="ai-output">{promo_response}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE ⑤ — DATABASE COPILOT
# ════════════════════════════════════════════════════════════════════════════
elif page == "🧠  Database Copilot":
    st.markdown("""
    <div class="page-header">
        <h2>🧠 Database Copilot</h2>
        <p>Your AI Ops Director — ask strategic workforce questions, generate impact reports</p>
    </div>
    """, unsafe_allow_html=True)

    # Build rich context (no PII)
    region_context = (
        df.groupby('Neighborhood')
        .agg(
            Headcount=('Volunteer_ID', 'count'),
            Avg_Att=('Attendance_Float', 'mean'),
            IMs=('Role', lambda x: (x == 'Intern-Manager').sum()),
            Vols=('Role', lambda x: (x == 'Volunteer').sum())
        )
        .reset_index()
        .to_csv(index=False)
    )

    top_skills = pd.Series(parse_skills(df['Skills'])).value_counts().head(20).to_string()

    COPILOT_SYSTEM = f"""You are the NGO Operations Director Copilot — a strategic AI advisor with full visibility into the volunteer database.

WORKFORCE SNAPSHOT:
- Total People: {len(df)} ({len(interns_df)} Intern-Managers, {len(volunteers_df)} Volunteers)
- Average Attendance: {avg_attendance:.0%}
- Regions Active: {len(neighborhoods)} ({', '.join(neighborhoods)})
- At-Risk (<50% att.): {len(df[df['Attendance_Float'] < 0.50])}
- Promotion Candidates (>82% att., Volunteer tier): {len(df[(df['Attendance_Float'] >= 0.82) & (df['Role'] == 'Volunteer')])}

REGIONAL BREAKDOWN:
{region_context}

TOP 20 SKILLS IN DATABASE:
{top_skills}

You answer STRATEGIC questions about: workforce density, regional coverage, simultaneous event capacity, skill gaps, deployment limits, ratio analysis, and operational readiness. Be precise, cite numbers from the data above, and give actionable recommendations. Never reveal individual PII in your responses."""

    if "copilot_msgs" not in st.session_state:
        st.session_state.copilot_msgs = []

    # Quick-fire suggested queries
    st.markdown('<div class="section-label">Quick Intelligence Queries</div>', unsafe_allow_html=True)
    suggestions = [
        ("🔍", "Which region has the weakest coverage?"),
        ("🚗", "How many drivers do we have per region?"),
        ("⚡", "Can we run 3 simultaneous events right now?"),
        ("📉", "Which skills are critically understaffed?"),
    ]
    cols = st.columns(len(suggestions))
    for col, (icon, q) in zip(cols, suggestions):
        if col.button(f"{icon} {q}", key=f"sugg_{q[:10]}"):
            st.session_state.copilot_msgs.append({"role": "user", "content": q})
            with st.spinner("Ops Director analyzing..."):
                messages = [{"role": "system", "content": COPILOT_SYSTEM}] + st.session_state.copilot_msgs
                res = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=1024)
                ai_reply = res.choices[0].message.content
                st.session_state.copilot_msgs.append({"role": "assistant", "content": ai_reply})
            st.rerun()

    st.markdown("---")

    # Chat history
    for msg in st.session_state.copilot_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your Ops Director anything about the workforce..."):
        st.session_state.copilot_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            messages = [{"role": "system", "content": COPILOT_SYSTEM}] + st.session_state.copilot_msgs
            res = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=1024)
            ai_reply = res.choices[0].message.content
            st.markdown(ai_reply)
            st.session_state.copilot_msgs.append({"role": "assistant", "content": ai_reply})

    st.markdown("---")
    btn_left, btn_right = st.columns([1, 1])

    if btn_left.button("🗑️ Clear Chat", key="clear_copilot"):
        st.session_state.copilot_msgs = []
        st.rerun()

    if btn_right.button("📄 Generate Donor Impact Report", type="primary", key="impact_report"):
        with st.spinner("Generating donor-ready impact report..."):
            report_prompt = f"""
Generate a polished, donor-ready NGO Workforce Impact Report.

DATA:
- Total Workforce: {len(df)} people across {len(neighborhoods)} neighborhoods
- Intern-Managers (Leadership): {len(interns_df)}
- Field Volunteers: {len(volunteers_df)}
- Average Attendance Rate: {avg_attendance:.0%}
- At-Risk Volunteers: {len(df[df['Attendance_Float'] < 0.50])} (flagged for re-engagement)
- Top Skills: {', '.join(pd.Series(parse_skills(df['Skills'])).value_counts().head(8).index.tolist())}

REGIONAL BREAKDOWN:
{region_context}

Write a formal 1-page impact report with these sections:
1. **Executive Summary** — 3 sentences. No bullet points. Inspiring and factual.
2. **Workforce Strength** — Key statistics, formatted clearly.
3. **Regional Reach** — Top 3 regions highlighted. What we can achieve there.
4. **Operational Capacity** — What events we can run simultaneously, max deployment scenarios.
5. **Growth Trajectory** — 1 forward-looking paragraph about expansion potential.

Tone: professional, data-backed, inspiring to donors and stakeholders.
"""
            report = call_ai(report_prompt, system="You are a senior NGO communications strategist. Write polished, donor-appropriate impact reports.")

        st.markdown("### 📄 Donor-Ready Impact Report")
        st.markdown(f'<div class="ai-output">{report}</div>', unsafe_allow_html=True)