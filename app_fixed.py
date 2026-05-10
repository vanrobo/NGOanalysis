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
    page_icon="ðŸ¤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# â”€â”€â”€ NEIGHBORHOOD COORDS (Delhi) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€â”€ API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
if not api_key:
    st.error("GROQ_API_KEY not configured. Please add it to your .env or secrets.")
    st.stop()

client = Groq(api_key=api_key)
MODEL_SMALL = "llama-3.1-8b-instant"
MODEL_LARGE = "llama-3.3-70b-versatile"

def call_ai(prompt, system="", max_tokens=2048, model=MODEL_SMALL):
    msgs =[]
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return client.chat.completions.create(model=model, messages=msgs, max_tokens=max_tokens).choices[0].message.content


# â”€â”€â”€ DATA PROCESSING â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@st.cache_data
def process_data(raw_df):
    df = raw_df.copy()
    
    # Normalize columns
    df.columns =[c.strip() for c in df.columns]
    
    # Handle missing names safely
    df['First_Name'] = df['First_Name'].fillna('')
    df['Last_Name'] = df['Last_Name'].fillna('')
    df['Full_Name'] = df['First_Name'].astype(str).str.strip() + " " + df['Last_Name'].astype(str).str.strip()
    
    # Robust Attendance
    if 'Attendance_Rate' in df.columns:
        df['Att_Val'] = pd.to_numeric(
            df['Attendance_Rate'].astype(str).str.replace('%', '', regex=False), errors='coerce'
        ).fillna(0)
        df['Att_Float'] = df['Att_Val'] / 100.0 if df['Att_Val'].max() > 1.0 else df['Att_Val']
    else:
        df['Att_Float'] = 0.0

    # FLATTEN HIERARCHY: Everyone is simply a Volunteer
    df['Role'] = 'Volunteer'
        
    if 'Neighborhood' not in df.columns:
        areas =['Paschim Vihar', 'Rohini', 'Dwarka', 'Janakpuri', 'Pitampura', 'Saket']
        df['Neighborhood'] = [areas[i % len(areas)] for i in range(len(df))]

    # Distinguish between Volunteers and Interns (20% Interns)
    if 'Type' not in df.columns:
        df['Type'] = ['Intern' if i % 5 == 0 else 'Volunteer' for i in range(len(df))]
        
    return df

def parse_skills(series):
    out =[]
    for v in series.dropna():
        out.extend([s.strip() for s in str(v).split(';') if s.strip()])
    return out


# â”€â”€â”€ SIDEBAR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        
    with st.expander("Required CSV Columns"):
        st.caption("""
        **Required:**
        Volunteer_ID, First_Name, Last_Name, Phone_Number, Email, Skills, Interests, Has_Vehicle, Attendance_Rate, Preferred_Days
        
        **Optional:**
        Neighborhood
        """)

# â”€â”€â”€ LANDING PAGE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if not uploaded_file:
    st.title("Welcome to the NGO Volunteer Portal")
    st.write("Please upload your volunteer database via the sidebar to activate the management modules.")
    st.divider()
    
    cols = st.columns(3)
    features =[
        ("Overview Dashboard", "High-level metrics, regional density, and skill inventory."),
        ("Event Deployment", "Plan local events and deploy the right volunteers based on data."),
        ("Unit Logistics", "Build squads and generate shift schedules."),
        ("Volunteer Analytics", "Identify skill gaps, track retention, and recognize top performers."),
        ("AI Assistant", "Chat with your data to extract strategic insights quickly.")
    ]
    
    for i, (name, desc) in enumerate(features):
        with cols[i % 3]:
            st.subheader(name)
            st.write(desc)
    st.stop()

# â”€â”€â”€ LOAD DATA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    df = process_data(pd.read_csv(uploaded_file))
except Exception as e:
    st.error(f"Error processing the CSV file: {e}")
    st.stop()

avg_att = df['Att_Float'].mean()
neighborhoods = sorted(df['Neighborhood'].unique().tolist())

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  01 Â· OVERVIEW DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
if page == "Overview Dashboard":
    st.title("Overview Dashboard")
    st.write(f"**Total Workforce:** {len(df)} personnel | **Regions Active:** {len(neighborhoods)}")
    st.divider()

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Workforce", len(df))
    k2.metric("Volunteers", len(df[df['Type'] == 'Volunteer']))
    k3.metric("Interns", len(df[df['Type'] == 'Intern']))
    k4.metric("Avg Attendance", f"{avg_att:.0%}")
    k5.metric("At Risk (<50% Att)", len(df[df['Att_Float'] < 0.5]))

    st.divider()

    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader("Workforce Density by Region & Type")
        region_type = df.groupby(['Neighborhood', 'Type']).size().reset_index(name='Count')
        fig = px.bar(
            region_type, 
            x='Neighborhood', 
            y='Count', 
            color='Type',
            barmode='group',
            color_discrete_map={'Volunteer': '#58a6ff', 'Intern': '#f5b041'}
        )
        fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Top Skills Inventory")
        sk = pd.Series(parse_skills(df['Skills'])).value_counts().head(15).reset_index()
        sk.columns =['Skill', 'Count']
        st.dataframe(sk, use_container_width=True, hide_index=True)

    st.divider()
    c3, c4 = st.columns([2, 3])

    with c3:
        st.subheader("Attendance Distribution by Type")
        df['Band'] = pd.cut(df['Att_Float'], bins=[0,.4,.6,.8,1.01], labels=['<40%','40-60%','60-80%','>80%'])
        bdata = df.groupby(['Band', 'Type']).size().reset_index(name='Count')
        fig2 = px.bar(
            bdata, 
            x='Band', 
            y='Count', 
            color='Type', 
            barmode='group',
            color_discrete_map={'Volunteer': '#47c283', 'Intern': '#e74c3c'}
        )
        fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

    with c4:
        st.subheader("Regional Readiness")
        readiness = df.groupby('Neighborhood').agg(
            Headcount=('Volunteer_ID','count'),
            Volunteers=('Type', lambda x: (x == 'Volunteer').sum()),
            Interns=('Type', lambda x: (x == 'Intern').sum()),
            Avg_Att=('Att_Float', lambda x: f"{x.mean():.0%}"),
        ).reset_index()
        st.dataframe(readiness, use_container_width=True, hide_index=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  02 Â· EVENT DEPLOYMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
elif page == "Event Deployment":
    st.title("Event Deployment Planning")
    st.write("Plan an event, set requirements, and generate a recommended deployment manifest.")

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        st.subheader("Event Parameters")
        sel_nbhd     = st.selectbox("Target Neighborhood",["All Regions"] + neighborhoods)
        event_name   = st.text_input("Event Name",   "Medical Camp")
        event_date   = st.text_input("Date & Time",  "Saturday, 10 AM â€“ 4 PM")
        target_count = st.number_input("Volunteers Needed", min_value=1, value=10, step=1)
        req_skills   = st.text_input("Required Skills", "First Aid, CPR")
        req_vehicle  = st.checkbox("Vehicle Required")

        # Now pulls from df instead of limited volunteers_df
        local_pool    = df if sel_nbhd == "All Regions" else df[df['Neighborhood'] == sel_nbhd].copy()
        local_avg     = local_pool['Att_Float'].mean() if len(local_pool) > 0 else 0.60
        buffer_target = int(target_count / local_avg) + 1 if local_avg > 0 else target_count * 2

        st.subheader("Capacity Check")
        b1, b2, b3 = st.columns(3)
        b1.metric("Local Avg Att.", f"{local_avg:.0%}")
        b2.metric("Target (Buffer)",  buffer_target)
        b3.metric("Available Pool",      len(local_pool))

        if len(local_pool) < buffer_target:
            st.warning(f"Available pool is insufficient. You may need to pull from other regions.")
        else:
            st.success(f"Pool sufficient to cover expected attendance drop-offs.")

    with c_right:
        st.subheader("Volunteer Map & Regional Insights")
        map_rows =[]
        for nbhd in neighborhoods:
            sub   = df[df['Neighborhood'] == nbhd]
            coord = NBHD_COORDS.get(nbhd)
            if coord:
                is_sel = sel_nbhd == nbhd or sel_nbhd == "All Regions"
                map_rows.append({
                    'Neighborhood': nbhd, 'lat': coord[0], 'lon': coord[1],
                    'Volunteers': len(sub[sub['Type'] == 'Volunteer']),
                    'Interns': len(sub[sub['Type'] == 'Intern']),
                    'Total': len(sub),
                    'Avg Att': f"{sub['Att_Float'].mean():.0%}" if len(sub) > 0 else 'N/A',
                    'Status': 'Target Area' if is_sel else 'Outside',
                })
        mdf = pd.DataFrame(map_rows)
        if len(mdf) > 0:
            fig_map = px.scatter_mapbox(
                mdf, lat='lat', lon='lon', size='Total', color='Status',
                hover_name='Neighborhood',
                hover_data={'lat':False,'lon':False,'Volunteers':True,'Interns':True,'Avg Att':True,'Status':False},
                size_max=38, zoom=10,
                center=dict(lat=28.635, lon=77.135),
                mapbox_style='carto-positron',
                color_discrete_map={'Target Area': '#58a6ff', 'Outside': '#afb8c1'}
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
            st.plotly_chart(fig_map, use_container_width=True)

        if sel_nbhd != "All Regions":
            st.subheader(f"Regional Drill-down: {sel_nbhd}")
            reg_sub = df[df['Neighborhood'] == sel_nbhd]
            s1, s2, s3 = st.columns(3)
            s1.metric("Volunteers", len(reg_sub[reg_sub['Type'] == 'Volunteer']))
            s2.metric("Interns", len(reg_sub[reg_sub['Type'] == 'Intern']))
            s3.metric("High Performers", len(reg_sub[reg_sub['Att_Float'] >= 0.8]))

        st.subheader(f"Available Pool â€” {sel_nbhd}")
        st.dataframe(
            local_pool[['Volunteer_ID','Full_Name','Type','Skills','Attendance_Rate','Preferred_Days']],
            use_container_width=True, hide_index=True, height=250
        )

    st.divider()

    if st.button("Generate Deployment Plan", type="primary"):
        with st.spinner("Analyzing pool and building deployment plan..."):
            safe = local_pool[['Volunteer_ID','Skills','Has_Vehicle','Attendance_Rate','Preferred_Days','Neighborhood']].copy()
            ai_out = call_ai(f"""
EVENT: {event_name} | DATE: {event_date} | REGION: {sel_nbhd}
TARGET: {target_count} | BUFFER TARGET: {buffer_target} (local avg {local_avg:.0%})
REQUIRED SKILLS: {req_skills} | VEHICLE: {req_vehicle}

POOL (no PII):
{safe.to_csv(index=False)}

OUTPUT â€” use these exact section headers:

## DEPLOYMENT MANIFEST
List exactly {buffer_target} Volunteer IDs. prioritize Volunteers over Interns. Brief rationale (2 sentences).

## ROLE ASSIGNMENT
Markdown table: Volunteer_ID | Event Task | Reason (note if they are an Intern/Volunteer)

## COMMUNICATION DRAFT
Ready-to-send broadcast message for volunteers. Max 150 words. Include: event, date, task, report time, what to bring.

## RISK FLAGS
Gaps, insufficient pool warnings, cross-region pull recommendations.
""", "You are a professional NGO coordinator planning an event deployment.", model=MODEL_LARGE)

        st.info("AI Deployment Plan Generated")
        st.markdown(ai_out)

        st.subheader("Contact List for Assigned Volunteers")
        found = list(set(re.findall(r'V-\d{3}', ai_out)))
        if found:
            contacts = df[df['Volunteer_ID'].isin(found)][['Volunteer_ID','Full_Name','Type','Phone_Number','Email','Skills','Has_Vehicle','Neighborhood']
            ].copy()
            st.dataframe(contacts, use_container_width=True, hide_index=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  03 Â· UNIT LOGISTICS (CAREER GROWTH HUB)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
elif page == "Unit Logistics":
    st.title("Volunteer Growth Hub")
    st.write("Empowering our workforce through AI-driven career coaching and skill development.")

    ch1, ch2, ch3 = st.tabs(["ðŸŽ“ Career Advisor", "ðŸ›£ï¸ Skill Roadmap", "ðŸŽ¤ Mock Interviewer"])

    with ch1:
        st.subheader("Personalized Career Path Advisor")
        st.write("Get AI recommendations for your professional journey based on your volunteer experience.")
        career_volunteer = st.selectbox("Select Volunteer for Career Advice:", df['Full_Name'].unique(), key="career_select")
        if career_volunteer and st.button("ðŸš€ Generate Career Paths", key="career_btn"):
            person = df[df['Full_Name'] == career_volunteer].iloc[0]
            with st.spinner("Analyzing career opportunities..."):
                career_prompt = f"""
                Volunteer: {person['Full_Name']}
                Type: {person['Type']}
                Skills: {person['Skills']}
                Interests: {person['Interests']}
                Attendance: {person['Attendance_Rate']}
                
                Based on this profile, suggest 3 career paths (e.g., NGO Management, Public Relations, Operations) 
                and explain how their volunteer work at our NGO prepares them for these roles.
                """
                response = call_ai(career_prompt, "You are a professional career coach and NGO advisor.", model=MODEL_LARGE)
                st.markdown(response)

    with ch2:
        st.subheader("ðŸ›£ï¸ Personalized Skill Development Roadmap")
        st.write("A 6-month AI-generated learning path tailored to your professional goals.")
        roadmap_volunteer = st.selectbox("Select Volunteer for Skill Roadmap:", df['Full_Name'].unique(), key="roadmap_select")
        goal = st.text_input("What is your ultimate professional goal?", value="Project Management in Social Sector")
        
        if roadmap_volunteer and st.button("ðŸ“š Build My Learning Path", key="roadmap_btn"):
            person = df[df['Full_Name'] == roadmap_volunteer].iloc[0]
            with st.spinner("Creating roadmap..."):
                roadmap_prompt = f"""
                Volunteer: {person['Full_Name']}
                Current Skills: {person['Skills']}
                Goal: {goal}
                
                Create a 6-month roadmap with month-by-month actionable steps, free resources, and skill milestones.
                """
                response = call_ai(roadmap_prompt, "You are a professional skill development coach.", model=MODEL_LARGE)
                st.markdown(response)

    with ch3:
        st.subheader("ðŸŽ¤ AI Mock Interviewer")
        st.write("Practice for your next professional role with real-time AI feedback.")
        interview_volunteer = st.selectbox("Select Volunteer for Interview:", df['Full_Name'].unique(), key="interview_select")
        target_role = st.text_input("What role are you interviewing for?", value="Program Coordinator")
        
        if interview_volunteer and st.button("Generate Interview Question", key="interview_btn"):
            person = df[df['Full_Name'] == interview_volunteer].iloc[0]
            with st.spinner("Preparing question..."):
                int_prompt = f"Volunteer: {person['Full_Name']}, Skills: {person['Skills']}. Target Role: {target_role}. Ask one tough behavioral interview question."
                st.session_state["current_question"] = call_ai(int_prompt, "You are an NGO hiring manager.", model=MODEL_SMALL)
                
        if "current_question" in st.session_state:
            st.info(st.session_state["current_question"])
            user_answer = st.text_area("Your Answer:")
            if st.button("Evaluate Answer", key="eval_btn"):
                with st.spinner("Evaluating..."):
                    eval_prompt = f"Question: {st.session_state['current_question']}\nAnswer: {user_answer}. Evaluate the answer and give constructive feedback."
                    eval_res = call_ai(eval_prompt, "You are an NGO hiring manager.", model=MODEL_LARGE)
                    st.success(eval_res)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  04 Â· VOLUNTEER ANALYTICS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
elif page == "Volunteer Analytics":
    st.title("Volunteer Analytics")
    st.write("Analyze regional skill gaps, identify retention risks, and recognize top contributors.")

    t1, t2, t3 = st.tabs(["Skill Gaps", "At-Risk Volunteers", "Top Performers"])

    with t1:
        st.subheader("Skill Gap Matrix")
        g_skills = list(set(parse_skills(df['Skills'])))
        gap_rows =[]
        for reg in neighborhoods:
            rdf     = df[df['Neighborhood'] == reg]
            r_sk    = list(set(parse_skills(rdf['Skills'])))
            missing =[s for s in g_skills if s not in r_sk]
            gap_rows.append({'Region':reg,
                             'Volunteers': len(rdf[rdf['Type']=='Volunteer']),
                             'Interns': len(rdf[rdf['Type']=='Intern']),
                             'Skill Gaps':len(missing),
                             'Missing Skills': ', '.join(missing[:5])+('â€¦' if len(missing)>5 else '')})
        gap_df = pd.DataFrame(gap_rows).sort_values('Skill Gaps', ascending=False)

        g1, g2 = st.columns([2, 3])
        with g1:
            fig_g = px.bar(gap_df, x='Skill Gaps', y='Region', orientation='h', color_discrete_sequence=['#f5b041'])
            fig_g.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=320)
            st.plotly_chart(fig_g, use_container_width=True)
        with g2:
            st.dataframe(gap_df, use_container_width=True, hide_index=True, height=340)

        st.divider()
        st.subheader("Recruitment Campaign Builder")
        sel_reg = st.selectbox("Target Region", neighborhoods, key="gap_reg")
        if st.button("Generate Recruitment Material", type="primary", key="gap_btn"):
            row = gap_df[gap_df['Region']==sel_reg].iloc[0]
            with st.spinner("Drafting campaign..."):
                ai_out = call_ai(f"Region: {sel_reg} | Missing Skills: {row['Missing Skills']}. Draft social media post.", model=MODEL_LARGE)
                st.info("Materials Generated")
                st.markdown(ai_out)

    with t2:
        st.subheader("Retention & Re-engagement")
        thresh = st.slider("At-Risk Threshold (Attendance %)", 30, 70, 50, 5)
        churn  = df[df['Att_Float'] < thresh/100].sort_values('Att_Float')

        cc1, cc2 = st.columns([1, 3])
        with cc1:
            st.metric("At-Risk Total", len(churn))
            st.write(f"**{len(churn[churn['Type']=='Volunteer'])}** Volunteers | **{len(churn[churn['Type']=='Intern'])}** Interns")
            churn_by_type = churn.groupby('Type').size().reset_index(name='Count')
            fig_cr = px.pie(churn_by_type, values='Count', names='Type', hole=.4, color_discrete_map={'Volunteer':'#e74c3c','Intern':'#f5b041'})
            fig_cr.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig_cr, use_container_width=True)
        with cc2:
            st.dataframe(churn[['Volunteer_ID','Full_Name','Type','Neighborhood','Attendance_Rate']], use_container_width=True, hide_index=True, height=340)

        if len(churn) > 0:
            if st.button("Generate Re-engagement Strategy", type="primary", key="churn_btn"):
                with st.spinner("Building strategy..."):
                    ai_out = call_ai(f"We have {len(churn)} at-risk volunteers. Draft check-in message and 3 retention tactics.", model=MODEL_LARGE)
                    st.info("Strategy Generated")
                    st.markdown(ai_out)

    with t3:
        st.subheader("Top Performers Recognition")
        p_thresh   = st.slider("High Performer Threshold (%)", 70, 95, 85, 1)
        candidates = df[df['Att_Float'] >= p_thresh/100].sort_values('Att_Float', ascending=False)

        pp1, pp2 = st.columns([1, 2])
        with pp1:
            st.metric("Total High Performers", len(candidates))
            st.write(f"**{len(candidates[candidates['Type']=='Volunteer'])}** Volunteers | **{len(candidates[candidates['Type']=='Intern'])}** Interns")
            top10 = candidates.head(10)
            fig_p = px.bar(top10, x='Volunteer_ID', y='Att_Float', color='Type', color_discrete_map={'Volunteer':'#2ecc71','Intern':'#f5b041'})
            fig_p.update_layout(title='Top Attendance Scores', margin=dict(t=30, b=0, l=0, r=0), height=220)
            st.plotly_chart(fig_p, use_container_width=True)
        with pp2:
            st.dataframe(candidates[['Volunteer_ID','Full_Name','Type','Neighborhood','Attendance_Rate']], use_container_width=True, hide_index=True, height=340)

        if len(candidates) > 0:
            if st.button("Draft Recognition Briefing", type="primary", key="promo_btn"):
                with st.spinner("Drafting briefing..."):
                    ai_out = call_ai(f"Top performing volunteers (attendance â‰¥ {p_thresh}%). Draft thank you email and recognition brief.", model=MODEL_LARGE)
                    st.info("Briefing Generated")
                    st.markdown(ai_out)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  05 Â· AI ASSISTANT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
