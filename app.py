import streamlit as st
import pandas as pd
from groq import Groq
import os, re
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="NGO Volunteer Portal",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══ CRITICAL: Initialize Session State First ═══
if "active_events" not in st.session_state:
    st.session_state.active_events = {}
if "event_history" not in st.session_state:
    st.session_state.event_history = []
if "cop_msgs" not in st.session_state:
    st.session_state.cop_msgs = []
if "draft_plan" not in st.session_state:
    st.session_state.draft_plan = None
if "draft_vols" not in st.session_state:
    st.session_state.draft_vols = []
# New Session States for Shadowing & Cross-skilling
if "shadow_requests" not in st.session_state:
    st.session_state.shadow_requests = []
if "learning_skill_input" not in st.session_state:
    st.session_state.learning_skill_input = ""

def set_learning_skill(skill):
    """Callback to safely set text input value without throwing API exceptions"""
    st.session_state.learning_skill_input = skill

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


# ─── API ──────────────────────────────────────────────────────────────────────
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


# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
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

def generate_whatsapp_link(phone_number, message=""):
    """Helper to consistently generate WhatsApp links across the app"""
    try:
        phone = str(phone_number).replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            phone = '+91' + phone if len(phone) == 10 else '+' + phone
        else:
            phone = '+' + phone.lstrip('+')
        return f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"
    except:
        return ""


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("NGO Portal")
    
    # ═══ ROLE-BASED ACCESS CONTROL ═══
    user_role = st.radio("Login as:", ["Admin", "Volunteer"], label_visibility="visible")
    st.divider()
    
    # ═══ CONDITIONAL NAVIGATION ═══
    if user_role == "Admin":
        page = st.radio("Navigation",[
            "Overview Dashboard",
            "Event Deployment",
            "Career Growth Hub",
            "Volunteer Analytics",
            "AI Assistant",
            "Event Transparency",
        ])
    else:  # Volunteer
        page = st.radio("Navigation",[
            "Volunteer View",
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

# ─── LANDING PAGE ────────────────────────────────────────────────────────────
if not uploaded_file:
    st.title("Welcome to the NGO Volunteer Portal")
    st.write("Please upload your volunteer database via the sidebar to activate the management modules.")
    st.divider()
    
    cols = st.columns(3)
    features =[
        ("Overview Dashboard", "High-level metrics, regional density, and skill inventory."),
        ("Event Deployment", "Plan local events and deploy the right volunteers based on data."),
        ("Career Growth Hub", "Personalized career advising, skill roadmaps, and mock interviews."),
        ("Volunteer Analytics", "Identify skill gaps, track retention, and recognize top performers."),
        ("AI Assistant", "Chat with your data to extract strategic insights quickly.")
    ]
    
    for i, (name, desc) in enumerate(features):
        with cols[i % 3]:
            st.subheader(name)
            st.write(desc)
    st.stop()

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    df = process_data(pd.read_csv(uploaded_file))
except Exception as e:
    st.error(f"Error processing the CSV file: {e}")
    st.stop()

# Calculate event_count per volunteer from history
event_counts = {}
for event_record in st.session_state.event_history:
    for vol_id in event_record.get('attendees', []):
        event_counts[vol_id] = event_counts.get(vol_id, 0) + 1

df['Event_Count'] = df['Volunteer_ID'].map(lambda x: event_counts.get(x, 0))

avg_att = df['Att_Float'].mean()
neighborhoods = sorted(df['Neighborhood'].unique().tolist())

# ════════════════════════════════════════════════════════════════════════════
#  01 · OVERVIEW DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
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

# ════════════════════════════════════════════════════════════════════════════
#  02 · EVENT DEPLOYMENT
# ════════════════════════════════════════════════════════════════════════════
elif page == "Event Deployment":
    st.title("Event Deployment Planning")
    st.write("Plan an event, set requirements, and generate a recommended deployment manifest.")
    
    st.info(f"📊 Tracking: {len(st.session_state.active_events)} active events | {len(st.session_state.event_history)} completed events")

    # Display Pending Shadow Requests so Admin is aware
    pending_shadows = [req for req in st.session_state.shadow_requests if req['status'] == 'Pending']
    if pending_shadows:
        with st.expander("🔔 Pending Shadow/Cross-Skill Requests (AI will try to pair them)", expanded=True):
            st.write("These volunteers requested to learn from experts. If they fit this event, the AI will prioritize assigning them together.")
            shadow_df = pd.DataFrame(pending_shadows)[['learner_name', 'expert_name', 'skill', 'status']]
            shadow_df.columns = ["Learner", "Expert Requested", "Skill to Learn", "Status"]
            st.dataframe(shadow_df, use_container_width=True, hide_index=True)

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        st.subheader("Event Parameters")
        sel_nbhd     = st.selectbox("Target Neighborhood",["All Regions"] + neighborhoods)
        event_name   = st.text_input("Event Name",   "Medical Camp")
        event_date   = st.text_input("Date & Time",  "Saturday, 10 AM - 4 PM")
        target_count = st.number_input("Volunteers Needed", min_value=1, value=10, step=1)
        req_skills   = st.text_input("Required Skills", "First Aid, CPR")
        req_vehicle  = st.checkbox("Vehicle Required")

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
            
        if st.button("Generate Deployment Plan", type="primary"):
            with st.spinner("Analyzing pool and building deployment plan..."):
                safe = local_pool[['Volunteer_ID','Full_Name','Skills','Has_Vehicle','Attendance_Rate','Preferred_Days','Neighborhood','Event_Count']].copy()
                
                shadow_context = "None at the moment."
                if pending_shadows:
                    shadow_context = "\n".join([f"- Learner: {s['learner_name']} ({s['learner_id']}) wants to shadow Expert: {s['expert_name']} ({s['expert_id']}) for skill: {s['skill']}" for s in pending_shadows])

                ai_out = call_ai(f"""
    EVENT: {event_name} | DATE: {event_date} | REGION: {sel_nbhd}
    TARGET: {target_count} | BUFFER TARGET: {buffer_target} (local avg {local_avg:.0%})
    REQUIRED SKILLS: {req_skills} | VEHICLE: {req_vehicle}

    POOL (no PII):
    {safe.to_csv(index=False)}

    PENDING SHADOW REQUESTS:
    {shadow_context}

    FAIRNESS & FUZZY MATCHING RULES:
    1. FUZZY SKILL MATCHING: If event requires "{req_skills}", accept volunteers with RELATED skills. 
       For example: "10th Grade Math" → person with "Engineering" or "Teaching" is eligible (skills transfer).
       Explain the skill match rationale.
    2. FAIRNESS CONSTRAINT: Volunteers with lower Event_Count should be prioritized to prevent burnout and ensure fairness.
    3. LEARNER-EXPERT PAIRING: If there are Pending Shadow Requests listed above, TRY TO INCLUDE THE PAIR in this deployment if they are available in the pool. Assign the learner as a "Shadow" role.

    OUTPUT - use these exact section headers:

    ## DEPLOYMENT MANIFEST
    List exactly {buffer_target} Volunteer IDs. Include rationale (2 sentences).

    ## ROLE ASSIGNMENT
    Markdown table: Volunteer_ID | Full_Name | Event Task | Role | Reason
    Note: Mark SHADOW roles for learners paired with experts.

    ## COMMUNICATION DRAFT
    Ready-to-send broadcast message. Max 150 words.

    ## FAIRNESS & SKILL MATCH NOTES
    Explain fuzzy matches, fairness decisions, and shadowing pairings.

    ## RISK FLAGS
    Gaps, insufficient pool warnings.
    """, "You are a professional NGO coordinator planning an event deployment with a commitment to fairness and skill development.", model=MODEL_LARGE)

                found = list(set(re.findall(r'V-\d{3}', ai_out)))
                # Store the AI output and found IDs in session state so they survive the next button click
                st.session_state.draft_plan = ai_out
                st.session_state.draft_vols = found
                st.rerun()

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

        st.subheader(f"Available Pool - {sel_nbhd}")
        st.dataframe(
            local_pool[['Volunteer_ID','Full_Name','Type','Skills','Attendance_Rate','Event_Count']],
            use_container_width=True, hide_index=True, height=250
        )

    # ─── DEPLOYMENT DRAFT RENDERER (Safe from button resets) ───
    if st.session_state.draft_plan:
        st.divider()
        st.info("AI Deployment Plan Generated - Please review and adjust the roster below before saving.")
        st.markdown(st.session_state.draft_plan)

        st.subheader("Contact List for Assigned Volunteers")
        
        # User can manually edit the selected volunteers
        default_selections = [v for v in st.session_state.draft_vols if v in local_pool['Volunteer_ID'].tolist()]
        if not default_selections:
            st.warning("⚠️ Could not extract specific volunteer IDs from AI output. Please select manually:")
            default_selections = local_pool['Volunteer_ID'].head(target_count).tolist()
            
        selected_vols = st.multiselect(
            "Final Volunteer Roster:",
            options=local_pool['Volunteer_ID'].tolist(),
            default=default_selections,
            format_func=lambda vid: f"{vid} - {local_pool[local_pool['Volunteer_ID']==vid]['Full_Name'].values[0] if len(local_pool[local_pool['Volunteer_ID']==vid]) > 0 else 'Unknown'}",
            key="final_vol_select"
        )
        
        if selected_vols:
            contacts = df[df['Volunteer_ID'].isin(selected_vols)][['Volunteer_ID','Full_Name','Type','Phone_Number','Skills','Neighborhood']].copy()
            
            # ═══ ADD WHATSAPP LINKS ═══
            contacts['WhatsApp_Link'] = contacts.apply(
                lambda row: generate_whatsapp_link(
                    row['Phone_Number'], 
                    f"Hi {row['Full_Name']}, you have been selected for {event_name} on {event_date}. Please confirm your availability. Thank you!"
                ), axis=1)
            
            st.dataframe(
                contacts,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "WhatsApp_Link": st.column_config.LinkColumn("WhatsApp Link", display_text="📱 Chat")
                }
            )
        
        st.write("")
        c_save1, c_save2 = st.columns([1, 5])
        
        with c_save1:
            if st.button("💾 Save & Publish", type="primary"):
                if not selected_vols:
                    st.error("Please select at least one volunteer.")
                else:
                    event_id = f"EVT_{(len(st.session_state.active_events) + len(st.session_state.event_history) + 1):03d}"
                    st.session_state.active_events[event_id] = {
                        'name': event_name,
                        'date': event_date,
                        'neighborhood': sel_nbhd,
                        'target_count': target_count,
                        'required_skills': req_skills,
                        'vehicle_required': req_vehicle,
                        'assigned_volunteers': selected_vols,
                        'plan': st.session_state.draft_plan,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Mark fulfilled shadow requests
                    for req in st.session_state.shadow_requests:
                        if req['status'] == 'Pending' and req['learner_id'] in selected_vols and req['expert_id'] in selected_vols:
                            req['status'] = f'Fulfilled (Event {event_id})'

                    st.session_state.draft_plan = None
                    st.session_state.draft_vols = []
                    st.success(f"✅ Event {event_id} successfully saved!")
                    st.balloons()
                    st.rerun()
                    
        with c_save2:
            if st.button("❌ Cancel Draft"):
                st.session_state.draft_plan = None
                st.session_state.draft_vols = []
                st.rerun()

    # ─── MANAGE ACTIVE EVENTS ───
    st.divider()
    st.subheader("📋 Manage Active Events")
    
    if st.session_state.active_events:
        c_active1, c_active2 = st.columns([2, 1])
        with c_active1:
            for evt_id, evt_data in st.session_state.active_events.items():
                st.markdown(f"**{evt_id}: {evt_data['name']}** - {evt_data['neighborhood']} ({len(evt_data['assigned_volunteers'])} assigned)")
                
        with c_active2:
            event_to_close = st.selectbox("Select event to close/complete:", list(st.session_state.active_events.keys()))
            if st.button("✅ Mark as Completed", type="secondary"):
                event_data = st.session_state.active_events.pop(event_to_close)
                completed_event = {
                    'event_id': event_to_close,
                    **event_data,
                    'completed_at': datetime.now().isoformat(),
                    'attendees': event_data['assigned_volunteers']
                }
                st.session_state.event_history.append(completed_event)
                st.success(f"Event {event_to_close} moved to history!")
                st.rerun()
    else:
        st.info("No active events. Generate and save an event plan above.")


# ════════════════════════════════════════════════════════════════════════════
#  03 · CAREER GROWTH HUB
# ════════════════════════════════════════════════════════════════════════════
elif page == "Career Growth Hub":
    st.title("Volunteer Growth Hub")
    st.write("Empowering our workforce through AI-driven career coaching and skill development.")

    ch1, ch2, ch3 = st.tabs(["🎓 Career Advisor", "🛣️ Skill Roadmap", "🎤 Mock Interviewer"])

    with ch1:
        st.subheader("Personalized Career Path Advisor")
        st.write("Get AI recommendations for your professional journey based on your volunteer experience.")
        career_volunteer = st.selectbox("Select Volunteer for Career Advice:", df['Full_Name'].unique(), key="career_select")
        if career_volunteer and st.button("🚀 Generate Career Paths", key="career_btn"):
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
        st.subheader("🛣️ Personalized Skill Development Roadmap")
        st.write("A 6-month AI-generated learning path tailored to your professional goals.")
        roadmap_volunteer = st.selectbox("Select Volunteer for Skill Roadmap:", df['Full_Name'].unique(), key="roadmap_select")
        goal = st.text_input("What is your ultimate professional goal?", value="Project Management in Social Sector")
        
        if roadmap_volunteer and st.button("📚 Build My Learning Path", key="roadmap_btn"):
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
        st.subheader("🎤 AI Mock Interviewer")
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

# ════════════════════════════════════════════════════════════════════════════
#  04 · VOLUNTEER ANALYTICS (Admin Interactions Added)
# ════════════════════════════════════════════════════════════════════════════
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
                             'Missing Skills': ', '.join(missing[:5])+('...' if len(missing)>5 else '')})
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
            st.write("**Direct Action: Nudge At-Risk Volunteers**")
            churn_display = churn[['Volunteer_ID','Full_Name','Type','Phone_Number','Attendance_Rate']].copy()
            churn_display['Quick_Message'] = churn_display.apply(
                lambda row: generate_whatsapp_link(row['Phone_Number'], f"Hi {row['Full_Name']}, we missed you at recent events! We value your help at the NGO and hope to see you soon. Let us know if you need anything."), 
                axis=1
            )
            st.dataframe(
                churn_display, 
                use_container_width=True, 
                hide_index=True, 
                height=340,
                column_config={"Quick_Message": st.column_config.LinkColumn("Message", display_text="📱 Reach Out")}
            )

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
            st.write("**Direct Action: Congratulate Top Performers**")
            top_display = candidates[['Volunteer_ID','Full_Name','Type','Phone_Number','Attendance_Rate']].copy()
            top_display['Quick_Message'] = top_display.apply(
                lambda row: generate_whatsapp_link(row['Phone_Number'], f"Hi {row['Full_Name']}, thank you for being a top performer at our NGO! Your dedication is truly inspiring."), 
                axis=1
            )
            st.dataframe(
                top_display, 
                use_container_width=True, 
                hide_index=True, 
                height=340,
                column_config={"Quick_Message": st.column_config.LinkColumn("Message", display_text="🌟 Congratulate")}
            )

# ════════════════════════════════════════════════════════════════════════════
#  05 · AI ASSISTANT
# ════════════════════════════════════════════════════════════════════════════
elif page == "AI Assistant":
    st.title("AI Assistant")
    st.write("Chat with an AI assistant that understands your workforce data.")

    # GRANULAR CONTEXT: Provide enough data to avoid hallucinations
    region_ctx = df.groupby('Neighborhood').agg(Count=('Volunteer_ID','count'), Avg_Att=('Att_Float','mean')).reset_index().to_csv(index=False)
    intern_list = df[df['Type'] == 'Intern'].sort_values('Att_Float', ascending=False)[
        ['Volunteer_ID', 'Full_Name', 'Attendance_Rate', 'Neighborhood', 'Skills']
    ].to_csv(index=False)
    top_vols = df[df['Type'] == 'Volunteer'].sort_values('Att_Float', ascending=False).head(30)[
        ['Volunteer_ID', 'Full_Name', 'Attendance_Rate', 'Neighborhood', 'Skills']
    ].to_csv(index=False)

    SYSTEM = f"""You are a strict NGO Data Analyst. 
CONTEXT:
- Total Workforce: {len(df)}
- Regional Overview:
{region_ctx}

LIST OF ALL INTERNS:
{intern_list}

TOP 30 VOLUNTEERS:
{top_vols}

STRICT RULES:
1. ONLY use names and IDs from the lists above.
2. If a person is NOT in the lists, state you don't have their individual record.
3. NEVER invent names, IDs, or statistics.
4. If asked for "90%+" and someone is in the list with that score, list them.
5. Accuracy is more important than speed."""

    for msg in st.session_state.cop_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about your data..."):
        st.session_state.cop_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            ai_reply = call_ai(prompt, SYSTEM, model=MODEL_LARGE)
            st.markdown(ai_reply)
            st.session_state.cop_msgs.append({"role": "assistant", "content": ai_reply})

    st.divider()
    d1, d2 = st.columns(2)
    if d1.button("Clear Chat", key="clear_cop"):
        st.session_state.cop_msgs = []
        st.rerun()
    if d2.button("Generate Status Report", type="primary", key="donor_rpt"):
        with st.spinner("Compiling report..."):
            report = call_ai("Write a professional NGO Workforce Status Report based on the provided data.", SYSTEM, model=MODEL_LARGE)
            st.subheader("Workforce Status Report")
            st.markdown(report)

# ════════════════════════════════════════════════════════════════════════════
#  06 · EVENT TRANSPARENCY (Admin Only)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Event Transparency":
    st.title("📊 Event Transparency Dashboard")
    st.write("Track all active and historical events with volunteer participation metrics.")
    
    st.info(f"📊 Current Session: {len(st.session_state.active_events)} active | {len(st.session_state.event_history)} completed")
    
    t1, t2, t3 = st.tabs(["Active Events", "Event History", "Participation Analytics"])
    
    with t1:
        st.subheader("🔴 Currently Active Events")
        if st.session_state.active_events:
            for evt_id, evt_data in st.session_state.active_events.items():
                with st.expander(f"{evt_id}: {evt_data['name']} - {evt_data['neighborhood']}", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Date", evt_data['date'])
                    col2.metric("Target", evt_data['target_count'])
                    col3.metric("Assigned", len(evt_data.get('assigned_volunteers', [])))
                    col4.metric("Skills Needed", evt_data['required_skills'][:25] + "..." if len(evt_data['required_skills']) > 25 else evt_data['required_skills'])
                    st.markdown("**Assigned Volunteers:**")
                    if evt_data.get('assigned_volunteers'):
                        assigned_details = df[df['Volunteer_ID'].isin(evt_data['assigned_volunteers'])][['Volunteer_ID', 'Full_Name', 'Type', 'Event_Count', 'Attendance_Rate']]
                        st.dataframe(assigned_details, use_container_width=True, hide_index=True)
                    else:
                        st.write("No volunteers assigned")
        else:
            st.info("No active events. Create one in the Event Deployment page.")
    
    with t2:
        st.subheader("✅ Event History & Completion Records")
        if st.session_state.event_history:
            for idx, event_rec in enumerate(reversed(st.session_state.event_history)):
                with st.expander(f"{event_rec['event_id']}: {event_rec['name']} - Completed {event_rec['completed_at'][:10]}", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Neighborhood", event_rec['neighborhood'])
                    col2.metric("Target", event_rec['target_count'])
                    col3.metric("Attended", len(event_rec.get('attendees', [])))
                    attendee_count = len(event_rec.get('attendees', []))
                    target = event_rec.get('target_count', 1)
                    col4.metric("Attendance %", f"{(attendee_count / target * 100):.0f}%" if target > 0 else "N/A")
                    st.markdown("**Attendee Details:**")
                    if event_rec.get('attendees'):
                        attendee_details = df[df['Volunteer_ID'].isin(event_rec['attendees'])][['Volunteer_ID', 'Full_Name', 'Type', 'Attendance_Rate']]
                        st.dataframe(attendee_details, use_container_width=True, hide_index=True)
                    else:
                        st.write("No attendee records")
        else:
            st.info("No completed events yet.")
    
    with t3:
        st.subheader("📈 Participation & Fairness Analytics")
        
        if st.session_state.event_history:
            participation = {}
            for event_rec in st.session_state.event_history:
                for vol_id in event_rec.get('attendees', []):
                    participation[vol_id] = participation.get(vol_id, 0) + 1
            
            if participation:
                part_df = pd.DataFrame(list(participation.items()), columns=['Volunteer_ID', 'Events_Attended'])
                part_df = part_df.merge(df[['Volunteer_ID', 'Full_Name', 'Type']], on='Volunteer_ID', how='left')
                part_df = part_df.sort_values('Events_Attended', ascending=False)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Total Events Completed", len(st.session_state.event_history))
                    st.metric("Volunteers Engaged", len(participation))
                    avg_participation = part_df['Events_Attended'].mean()
                    st.metric("Avg Events per Volunteer", f"{avg_participation:.1f}")
                
                with col_b:
                    fig_part = px.bar(part_df.head(15), x='Full_Name', y='Events_Attended', color='Type', 
                                     color_discrete_map={'Volunteer': '#58a6ff', 'Intern': '#f5b041'})
                    fig_part.update_layout(title='Top Participants', xaxis_title='', yaxis_title='Events Attended', 
                                          margin=dict(t=30, b=0, l=0, r=0), height=350)
                    st.plotly_chart(fig_part, use_container_width=True)
                
                st.subheader("Participation Summary")
                st.dataframe(part_df, use_container_width=True, hide_index=True, height=400)
            else:
                st.info("No participation data yet. Complete events to see analytics.")
        else:
            st.info("No participation data yet. Complete events to see analytics.")

# ════════════════════════════════════════════════════════════════════════════
#  07 · VOLUNTEER VIEW (Volunteers Only)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Volunteer View":
    st.title("🙋 Volunteer Portal")
    st.write("Your personalized volunteer dashboard with event opportunities and growth paths.")
    
    st.subheader("👤 Login as Volunteer")
    logged_in_volunteer = st.selectbox(
        "Select your name:",
        sorted(df['Full_Name'].unique().tolist()),
        key="volunteer_login"
    )
    
    if logged_in_volunteer:
        vol_record = df[df['Full_Name'] == logged_in_volunteer].iloc[0]
        
        vt1, vt2, vt3 = st.tabs(["📋 My Profile & History", "📅 Open Events", "🎓 Shadowing & Cross-Skill Learning"])
        
        with vt1:
            st.subheader(f"Profile: {logged_in_volunteer}")
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown("**Basic Information**")
                st.write(f"**ID:** {vol_record['Volunteer_ID']}")
                st.write(f"**Type:** {vol_record['Type']}")
                st.write(f"**Neighborhood:** {vol_record['Neighborhood']}")
            
            with col_p2:
                st.markdown("**Performance Metrics**")
                st.metric("Attendance Rate", vol_record['Attendance_Rate'])
                st.metric("Events Attended", vol_record['Event_Count'])
                st.metric("Has Vehicle", "✅ Yes" if vol_record['Has_Vehicle'] == 'Yes' else "❌ No")
            
            st.divider()
            st.markdown("**Current Skills**")
            skills_list = [s.strip() for s in str(vol_record['Skills']).split(';') if s.strip()]
            if skills_list:
                skill_pills = " | ".join([f"🏷️ {skill}" for skill in skills_list])
                st.write(skill_pills)
            else:
                st.write("No skills listed")
            
            st.divider()
            st.markdown("**📊 My Event History**")
            
            attended_events = []
            for event_rec in st.session_state.event_history:
                if vol_record['Volunteer_ID'] in event_rec['attendees']:
                    attended_events.append({
                        'Event ID': event_rec['event_id'],
                        'Event Name': event_rec['name'],
                        'Date': event_rec['completed_at'][:10],
                        'Neighborhood': event_rec['neighborhood'],
                        'Role': 'Participant'
                    })
            
            if attended_events:
                st.dataframe(pd.DataFrame(attended_events), use_container_width=True, hide_index=True, height=250)
            else:
                st.info("No completed events yet. Check Open Events to join upcoming opportunities!")
        
        with vt2:
            st.subheader("📅 Available Event Opportunities")
            
            if st.session_state.active_events:
                for evt_id, evt_data in st.session_state.active_events.items():
                    is_assigned = vol_record['Volunteer_ID'] in evt_data['assigned_volunteers']
                    
                    col_e1, col_e2 = st.columns([4, 1])
                    with col_e1:
                        status_badge = "✅ You're Assigned!" if is_assigned else "🟡 Open"
                        st.markdown(f"### {evt_data['name']} {status_badge}")
                        st.write(f"**When:** {evt_data['date']} | **Where:** {evt_data['neighborhood']}")
                        st.write(f"**Skills Needed:** {evt_data['required_skills']}")
                    
                    with col_e2:
                        if is_assigned:
                            st.success("Assigned")
                        else:
                            st.info("Available")
                    st.divider()
            else:
                st.info("No open events at this time. Check back soon!")
        
        with vt3:
            st.subheader("🎓 What is Shadowing?")
            st.info("""
            **Shadowing** means you attend an event specifically to learn a new skill from an expert volunteer. 
            You will act as their assistant, watch how they handle tasks, and get real-world experience without the pressure of doing it alone!
            """)
            
            # Show My Shadowing Status
            my_shadow_requests = [req for req in st.session_state.shadow_requests if req['learner_id'] == vol_record['Volunteer_ID']]
            if my_shadow_requests:
                st.markdown("**Your Learning Requests:**")
                for req in my_shadow_requests:
                    if req['status'] == 'Pending':
                        st.warning(f"🕒 **Pending:** Waiting to shadow **{req['expert_name']}** for **{req['skill']}**. (Admin will pair you in an upcoming event!)")
                    else:
                        st.success(f"✅ **Completed:** Shadowed **{req['expert_name']}** for **{req['skill']}** ({req['status']})")
                st.divider()

            st.markdown("### Find an Expert to Learn From")
            st.text_input(
                "What skill would you like to learn?",
                placeholder="e.g., Java, First Aid, Teaching",
                value=st.session_state.learning_skill_input,
                key="learning_skill_widget"
            )
            # Sync the widget value back to session state to process search
            st.session_state.learning_skill_input = st.session_state.learning_skill_widget
            
            # Extract skills for quick buttons
            all_skills = set()
            for skills_str in df['Skills'].dropna():
                all_skills.update([s.strip() for s in str(skills_str).split(';')])
            
            st.markdown("**Or click a popular skill below:**")
            skill_cols = st.columns(4)
            for idx, skill in enumerate(sorted(all_skills)[:12]):
                with skill_cols[idx % 4]:
                    # Using callback to avoid exception
                    st.button(skill, key=f"btn_{idx}", on_click=set_learning_skill, args=(skill,))

            if st.session_state.learning_skill_input:
                current_skill = st.session_state.learning_skill_input
                with st.spinner("Finding experts..."):
                    experts = []
                    for _, expert in df.iterrows():
                        if current_skill.lower() in str(expert['Skills']).lower():
                            if expert['Volunteer_ID'] != vol_record['Volunteer_ID']:
                                experts.append(expert)
                    
                    if experts:
                        st.success(f"✅ Found {len(experts)} potential expert(s) who know '{current_skill}'!")
                        
                        for expert in experts[:5]: 
                            with st.expander(f"👨‍🏫 {expert['Full_Name']} - Events Attended: {expert['Event_Count']}", expanded=False):
                                st.write(f"**Neighborhood:** {expert['Neighborhood']}")
                                st.write(f"**Expertise:** {expert['Skills']}")
                                st.write(f"**Experience Level:** {'Expert (High Participation)' if expert['Event_Count'] >= 5 else 'Experienced' if expert['Event_Count'] >= 3 else 'Intermediate'}")
                                
                                # Check if already requested
                                already_requested = any(req['expert_id'] == expert['Volunteer_ID'] and req['skill'] == current_skill and req['status'] == 'Pending' for req in my_shadow_requests)
                                
                                if already_requested:
                                    st.info("🕒 You have already requested to shadow this expert.")
                                else:
                                    if st.button(f"Request to Shadow {expert['Full_Name']}", key=f"shadow_{expert['Volunteer_ID']}"):
                                        st.session_state.shadow_requests.append({
                                            'learner_id': vol_record['Volunteer_ID'],
                                            'learner_name': vol_record['Full_Name'],
                                            'expert_id': expert['Volunteer_ID'],
                                            'expert_name': expert['Full_Name'],
                                            'skill': current_skill,
                                            'status': 'Pending'
                                        })
                                        st.success(f"✅ Request sent! Admin will try to pair you with {expert['Full_Name']} in an upcoming event.")
                                        st.rerun()
                    else:
                        st.warning(f"❌ No experts found for '{current_skill}' yet. Try another skill.")