import streamlit as st
import pandas as pd
from groq import Groq
import os, re
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

st.set_page_config(
    page_title="NGO Volunteer Portal",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# ─── API ─────────────────────────────────────────────────────────────────────
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    st.error("GROQ_API_KEY not configured. Please add it to your .env or secrets.")
    st.stop()

client = Groq(api_key=api_key)
MODEL       = "llama-3.1-8b-instant"
MODEL_LARGE = "llama-3.3-70b-versatile"

def call_ai(prompt, system="", max_tokens=2048, model=MODEL):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return client.chat.completions.create(model=model, messages=msgs, max_tokens=max_tokens).choices[0].message.content

# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
@st.cache_data
def process_data(raw_df):
    df = raw_df.copy()
    df.columns =[c.strip() for c in df.columns]
    df['First_Name'] = df['First_Name'].fillna('')
    df['Last_Name'] = df['Last_Name'].fillna('')
    df['Full_Name'] = df['First_Name'].astype(str).str.strip() + " " + df['Last_Name'].astype(str).str.strip()
    if 'Attendance_Rate' in df.columns:
        df['Att_Val'] = pd.to_numeric(df['Attendance_Rate'].astype(str).str.replace('%', '', regex=False), errors='coerce').fillna(0)
        df['Att_Float'] = df['Att_Val'] / 100.0 if df['Att_Val'].max() > 1.0 else df['Att_Val']
    else:
        df['Att_Float'] = 0.0
    df['Role'] = 'Volunteer'
    if 'Neighborhood' not in df.columns:
        areas =['Paschim Vihar', 'Rohini', 'Dwarka', 'Janakpuri', 'Pitampura', 'Saket']
        df['Neighborhood'] = [areas[i % len(areas)] for i in range(len(df))]
    return df

def parse_skills(series):
    out =[]
    for v in series.dropna():
        out.extend([s.strip() for s in str(v).split(';') if s.strip()])
    return out

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("NGO Portal")
    page = st.radio("Navigation",[
        "Overview Dashboard",
        "Event Deployment",
        "Unit Logistics",
        "Volunteer Analytics",
        "AI Assistant",
    ])
    st.divider()
    uploaded_file = st.file_uploader("Upload Volunteer Database (CSV)", type="csv")
    if uploaded_file:
        st.success("Database Active")

# ─── LANDING PAGE ────────────────────────────────────────────────────────────
if not uploaded_file:
    st.title("Welcome to the NGO Volunteer Portal")
    st.write("Please upload your volunteer database via the sidebar.")
    st.stop()

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
df = process_data(pd.read_csv(uploaded_file))
avg_att = df['Att_Float'].mean()
neighborhoods = sorted(df['Neighborhood'].unique().tolist())

# 01 · OVERVIEW DASHBOARD
if page == "Overview Dashboard":
    st.title("Overview Dashboard")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Workforce", len(df))
    k2.metric("Avg Attendance", f"{avg_att:.0%}")
    k3.metric("Regions Active", len(neighborhoods))
    k4.metric("At Risk (<50%)", len(df[df['Att_Float'] < 0.5]))
    
    st.divider()
    st.subheader("🌐 Strategic Workforce Impact")
    if st.button("Generate Impact Report", type="primary"):
        with st.spinner("Analyzing..."):
            report = call_ai(f"Analyze workforce of {len(df)} volunteers with avg attendance {avg_att:.1%}.", "You are an NGO strategist.")
            st.markdown(report)

# 02 · EVENT DEPLOYMENT
elif page == "Event Deployment":
    st.title("Event Deployment")
    sel_nbhd = st.selectbox("Neighborhood", ["All Regions"] + neighborhoods)
    event_name = st.text_input("Event Name", "Anemia Day Camp")
    target_count = st.number_input("Volunteers Needed", min_value=1, value=10)
    
    if st.button("Generate Deployment Plan", type="primary"):
        with st.spinner("Planning..."):
            ai_out = call_ai(f"Plan {event_name} for {target_count} volunteers in {sel_nbhd}.", "You are an NGO coordinator.")
            st.markdown(ai_out)

# 03 · UNIT LOGISTICS
elif page == "Unit Logistics":
    st.title("Unit Logistics")
    lu1, lu2 = st.tabs(["Squad Planning", "Wellbeing Check"])
    with lu1:
        st.subheader("Squad & Shift Planning")
        if st.button("Generate Squads"):
            st.write("Squad logic executed.")
    with lu2:
        st.subheader("🧘 Wellbeing Predictor")
        wb_volunteer = st.selectbox("Select Volunteer:", df['Full_Name'].unique())
        if st.button("Analyze Wellbeing"):
            res = call_ai(f"Analyze wellbeing for {wb_volunteer}.", "You are a wellbeing officer.")
            st.markdown(res)

# 04 · VOLUNTEER ANALYTICS (GROWTH HUB)
elif page == "Volunteer Analytics":
    st.title("The Growth Hub")
    gh1, gh2, gh3, gh4 = st.tabs(["Workforce Stats", "Career Advisor", "Skill Roadmap", "Mock Interviewer"])
    with gh1:
        st.subheader("Workforce Stats")
        st.write(f"Total: {len(df)}")
    with gh2:
        st.subheader("🎓 Career Advisor")
        name = st.selectbox("Select Volunteer:", df['Full_Name'].unique(), key="gh2_name")
        if st.button("Generate Career Paths"):
            st.markdown(call_ai(f"Suggest career paths for {name}.", "You are a career advisor."))
    with gh3:
        st.subheader("🛣️ Skill Roadmap")
        name = st.selectbox("Select Volunteer:", df['Full_Name'].unique(), key="gh3_name")
        if st.button("Build Roadmap"):
            st.markdown(call_ai(f"Create roadmap for {name}.", "You are a coach."))
    with gh4:
        st.subheader("🎤 Mock Interviewer")
        name = st.selectbox("Select Volunteer:", df['Full_Name'].unique(), key="gh4_name")
        if st.button("Start Interview"):
            st.session_state.interview_q = call_ai(f"Ask {name} an interview question.", "You are a recruiter.")
        if "interview_q" in st.session_state:
            st.info(st.session_state.interview_q)

# 05 · AI ASSISTANT
elif page == "AI Assistant":
    st.title("AI Assistant")
    as1, as2 = st.tabs(["Data Copilot", "Skill Discovery"])
    with as1:
        if "cop_msgs" not in st.session_state: st.session_state.cop_msgs = []
        for m in st.session_state.cop_msgs:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Ask about data..."):
            st.session_state.cop_msgs.append({"role":"user","content":p})
            with st.chat_message("user"): st.markdown(p)
            with st.chat_message("assistant"):
                r = call_ai(p, "You are a data assistant.")
                st.markdown(r)
                st.session_state.cop_msgs.append({"role":"assistant","content":r})
    with as2:
        st.subheader("🕵️ Skill Discovery")
        name = st.text_input("Your Name:")
        if name:
            st.write(f"Hello {name}, let's find your hidden skills!")