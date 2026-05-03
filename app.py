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
MODEL  = "llama-3.3-70b-versatile"

def call_ai(prompt, system="", max_tokens=2048):
    msgs =[]
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=max_tokens).choices[0].message.content


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
        ("Unit Logistics", "Build squads and generate shift schedules."),
        ("Volunteer Analytics", "Identify skill gaps, track retention, and recognize top performers."),
        ("AI Assistant", "Chat with your data to extract strategic insights quickly.")
    ]
    
    for i, (name, desc) in enumerate(features):
        with cols[i % 3]:
            st.subheader(name)
            st.write(desc)
    st.stop()

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
try:
    df = process_data(pd.read_csv(uploaded_file))
except Exception as e:
    st.error(f"Error processing the CSV file: {e}")
    st.stop()

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
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Workforce", len(df))
    k2.metric("Avg Attendance", f"{avg_att:.0%}")
    k3.metric("Regions Active", len(neighborhoods))
    k4.metric("At Risk (<50% Att)", len(df[df['Att_Float'] < 0.5]))

    st.divider()

    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader("Volunteer Density by Region")
        region_data = df.groupby('Neighborhood').size().reset_index(name='Count')
        fig = go.Figure(go.Bar(
            name='Volunteers', 
            x=region_data['Neighborhood'], 
            y=region_data['Count'], 
            marker_color='#58a6ff'
        ))
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
        st.subheader("Attendance Distribution")
        bins  = pd.cut(df['Att_Float'], bins=[0,.4,.6,.8,1.01], labels=['<40%','40-60%','60-80%','>80%'])
        bdata = bins.value_counts().sort_index().reset_index()
        bdata.columns =['Band','Count']
        fig2 = go.Figure(go.Bar(
            x=bdata['Band'], y=bdata['Count'],
            text=bdata['Count'], textposition='auto',
            marker_color='#47c283'
        ))
        fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

    with c4:
        st.subheader("Regional Readiness")
        readiness = df.groupby('Neighborhood').agg(
            Headcount=('Volunteer_ID','count'),
            Avg_Att=('Att_Float', lambda x: f"{x.mean():.0%}"),
            At_Risk=('Att_Float', lambda x: (x<.5).sum()),
        ).reset_index()
        st.dataframe(readiness, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
#  02 · EVENT DEPLOYMENT
# ════════════════════════════════════════════════════════════════════════════
elif page == "Event Deployment":
    st.title("Event Deployment Planning")
    st.write("Plan an event, set requirements, and generate a recommended deployment manifest.")

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        st.subheader("Event Parameters")
        sel_nbhd     = st.selectbox("Target Neighborhood",["All Regions"] + neighborhoods)
        event_name   = st.text_input("Event Name",   "Medical Camp")
        event_date   = st.text_input("Date & Time",  "Saturday, 10 AM – 4 PM")
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
        st.subheader("Volunteer Map")
        map_rows =[]
        for nbhd in neighborhoods:
            sub   = df[df['Neighborhood'] == nbhd] # Using entire df fixes the low count issue
            coord = NBHD_COORDS.get(nbhd)
            if coord:
                is_sel = sel_nbhd == nbhd or sel_nbhd == "All Regions"
                map_rows.append({
                    'Neighborhood': nbhd, 'lat': coord[0], 'lon': coord[1],
                    'Count': len(sub),
                    'Avg Att': f"{sub['Att_Float'].mean():.0%}" if len(sub) > 0 else 'N/A',
                    'Status': 'Target Area' if is_sel else 'Outside',
                })
        mdf = pd.DataFrame(map_rows)
        if len(mdf) > 0:
            fig_map = px.scatter_mapbox(
                mdf, lat='lat', lon='lon', size='Count', color='Status',
                hover_name='Neighborhood',
                hover_data={'lat':False,'lon':False,'Count':True,'Avg Att':True,'Status':False},
                size_max=38, zoom=10,
                center=dict(lat=28.635, lon=77.135),
                mapbox_style='carto-positron',
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
            st.plotly_chart(fig_map, use_container_width=True)

        st.subheader(f"Available Roster — {sel_nbhd}")
        st.dataframe(
            local_pool[['Volunteer_ID','Full_Name','Skills','Has_Vehicle','Attendance_Rate','Preferred_Days']],
            use_container_width=True, hide_index=True, height=200
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

OUTPUT — use these exact section headers:

## DEPLOYMENT MANIFEST
List exactly {buffer_target} Volunteer IDs. Brief rationale (2 sentences).

## ROLE ASSIGNMENT
Markdown table: Volunteer_ID | Event Task | Reason

## COMMUNICATION DRAFT
Ready-to-send broadcast message for volunteers. Max 150 words. Include: event, date, task, report time, what to bring.

## RISK FLAGS
Gaps, insufficient pool warnings, cross-region pull recommendations.
""", "You are a professional NGO coordinator planning an event deployment.")

        st.info("AI Deployment Plan Generated")
        st.markdown(ai_out)

        st.subheader("Contact List for Assigned Volunteers")
        found = list(set(re.findall(r'V-\d{3}', ai_out)))
        if found:
            contacts = df[df['Volunteer_ID'].isin(found)][['Volunteer_ID','Full_Name','Phone_Number','Email','Skills','Has_Vehicle','Neighborhood']
            ].copy()
            st.dataframe(contacts, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
#  03 · UNIT LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Unit Logistics":
    st.title("Unit Logistics")
    st.write("Organize volunteers into squads, set shift schedules, and generate role playbooks.")

    c_left, c_right = st.columns([1, 2], gap="large")

    with c_left:
        st.subheader("Event Configuration")
        event_name   = st.text_input("Event Name",   "Annual Food Drive")
        event_dur    = st.selectbox("Duration", ["4 hours", "6 hours", "8 hours", "Full Day"])
        shift_size   = st.selectbox("Shift Blocks", ["2 hours", "4 hours", "6 hours"])
        nbhd_filter  = st.selectbox("Region Filter", ["All Regions"] + neighborhoods)
        max_slots    = st.number_input("Volunteer Slots Needed", min_value=5, value=30, step=5)
        squad_size   = st.number_input("Target Squad Size", min_value=2, value=10, step=1)
        roles_needed = st.multiselect("Event Roles",[
            "General Labor","Drivers","Medics","Food Handlers",
            "Coordinators","Registration","Security","Media",
        ], default=["General Labor","Drivers","Coordinators"])

    with c_right:
        st.subheader("Workforce Preview")
        filtered = df.copy() if nbhd_filter == "All Regions" else df[df['Neighborhood'] == nbhd_filter].copy()
        
        # LOGIC FIX: Base math on the slots needed, not the total database
        pool_size = len(filtered)
        actual_slots = min(int(max_slots), pool_size) # Don't request more than we have
        
        # Calculate exactly how many squads are needed for the requested slots
        n_squads = (actual_slots // squad_size) + (1 if actual_slots % squad_size > 0 else 0)
        n_squads = max(n_squads, 1)

        p1, p2, p3 = st.columns(3)
        p1.metric("Available in Region", pool_size)
        p2.metric("Event Slots", actual_slots)
        p3.metric("Required Squads", n_squads)

        # Show top candidates that will likely be picked
        top_candidates = filtered.sort_values('Att_Float', ascending=False).head(actual_slots)
        st.dataframe(
            top_candidates[['Volunteer_ID','Full_Name','Skills','Preferred_Days','Attendance_Rate']],
            use_container_width=True, hide_index=True, height=240
        )

        st.subheader("Event Squad Structure")
        
        # Build realistic chart data based on remainder math
        squad_sizes =[]
        rem = actual_slots
        for i in range(n_squads):
            if rem >= squad_size:
                squad_sizes.append(squad_size)
                rem -= squad_size
            elif rem > 0:
                squad_sizes.append(rem)
                
        sq_names =[f"Squad {chr(65+i)}" for i in range(len(squad_sizes))]
        
        fig_sq = go.Figure()
        fig_sq.add_bar(name='Volunteers', x=sq_names, y=squad_sizes, marker_color='#58a6ff')
        fig_sq.update_layout(
            barmode='stack', 
            title=f'{actual_slots} VOLUNTEERS ACROSS {n_squads} SQUADS', 
            margin=dict(t=30, b=0, l=0, r=0), 
            height=250,
            yaxis=dict(range=[0, squad_size + 2]) # Keep Y-axis scaled nicely
        )
        st.plotly_chart(fig_sq, use_container_width=True)

    st.divider()

    if st.button("Generate Squad Schedule", type="primary"):
        with st.spinner("Structuring squads and shifts..."):
            safe_pool = top_candidates[['Volunteer_ID','Skills','Preferred_Days','Att_Float']].copy()
            ai_out = call_ai(f"""
EVENT: {event_name} | DURATION: {event_dur} | SHIFT BLOCKS: {shift_size}
ROLES: {', '.join(roles_needed)}
RULE: Organize exactly {actual_slots} Volunteers into {n_squads} squads (max {squad_size} per squad).

POOL (Top {actual_slots} candidates):
{safe_pool.to_csv(index=False)}

OUTPUT — use these exact section headers:

## SQUAD STRUCTURE
Table: Squad Name | Member IDs | Role focus

## SHIFT SCHEDULE
Table: Block | Time | Squad | Task | Notes

## ROLE PLAYBOOK
For each role ({', '.join(roles_needed)}): 2-3 concise bullets detailing responsibilities.

## SUMMARY
A brief summary paragraph of the plan.
""", "You are a professional NGO coordinator specializing in squad logistics.")

        st.info("Squad Schedule Generated")
        st.markdown(ai_out)

        st.subheader("Selected Personnel Roster")
        found = list(set(re.findall(r'V-\d{3}', ai_out)))
        if found:
            roster = df[df['Volunteer_ID'].isin(found)][['Volunteer_ID','Full_Name','Phone_Number','Skills','Neighborhood']
            ].copy()
            st.dataframe(roster, use_container_width=True, hide_index=True)
# ════════════════════════════════════════════════════════════════════════════
#  04 · VOLUNTEER ANALYTICS
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
            gap_rows.append({'Region':reg,'Headcount':len(rdf),
                             'Skills Present':len(r_sk),'Skill Gaps':len(missing),
                             'Missing Skills': ', '.join(missing[:5])+('…' if len(missing)>5 else '')})
        gap_df = pd.DataFrame(gap_rows).sort_values('Skill Gaps', ascending=False)

        g1, g2 = st.columns([2, 3])
        with g1:
            fig_g = go.Figure(go.Bar(
                x=gap_df['Skill Gaps'], y=gap_df['Region'], orientation='h',
                text=gap_df['Skill Gaps'], textposition='auto',
                marker_color='#f5b041'
            ))
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
                ai_out = call_ai(f"""
Region: {sel_reg} | Current Headcount: {row['Headcount']} | Missing Skills: {row['Missing Skills']}

Draft recruitment materials to find volunteers with these specific skills.

## SOCIAL MEDIA POST
Engaging and professional. 100 words max. Include a call to action.

## OUTREACH CHANNELS
3 specific, actionable ideas to reach people with these skills in {sel_reg}.
""", "You are an NGO recruitment specialist.")
            st.info("Materials Generated")
            st.markdown(ai_out)

    with t2:
        st.subheader("Retention & Re-engagement")
        thresh = st.slider("At-Risk Threshold (Attendance %)", 30, 70, 50, 5)
        churn  = df[df['Att_Float'] < thresh/100].sort_values('Att_Float')

        cc1, cc2 = st.columns([1, 3])
        with cc1:
            st.metric("At-Risk Volunteers", len(churn), help=f"Below {thresh}% attendance")
            st.write(f"**{len(churn)/len(df):.0%}** of total workforce")
            
            churn_by_region = churn.groupby('Neighborhood').size().reset_index(name='Count')
            fig_cr = go.Figure(go.Bar(
                x=churn_by_region['Count'], 
                y=churn_by_region['Neighborhood'], 
                orientation='h',
                marker_color='#e74c3c'
            ))
            fig_cr.update_layout(title='By Region', margin=dict(t=30, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig_cr, use_container_width=True)

        with cc2:
            st.dataframe(
                churn[['Volunteer_ID','Full_Name','Neighborhood','Attendance_Rate','Skills']],
                use_container_width=True, hide_index=True, height=420
            )

        if len(churn) > 0:
            if st.button("Generate Re-engagement Strategy", type="primary", key="churn_btn"):
                with st.spinner("Building strategy..."):
                    safe_c = churn[['Volunteer_ID','Neighborhood','Skills','Attendance_Rate']].head(20)
                    ai_out = call_ai(f"""
We have {len(churn)} volunteers falling below our {thresh}% attendance threshold.

Sample profiles:
{safe_c.to_csv(index=False)}

## RE-ENGAGEMENT MESSAGE
Draft a warm, non-judgmental email or message checking in on them and inviting them back. 150 words max.

## RETENTION TACTICS
Provide 3 practical ideas to improve attendance among this group based on standard NGO best practices.
""", "You are a community engagement manager for an NGO.")
                st.info("Strategy Generated")
                st.markdown(ai_out)

    with t3:
        st.subheader("Top Performers Recognition")
        p_thresh   = st.slider("High Performer Threshold (%)", 70, 95, 85, 1)
        candidates = df[df['Att_Float'] >= p_thresh/100].sort_values('Att_Float', ascending=False)

        pp1, pp2 = st.columns([1, 2])
        with pp1:
            st.metric("Qualified Top Performers", len(candidates))
            
            top10 = candidates.head(10)
            fig_p = go.Figure(go.Bar(
                x=top10['Volunteer_ID'], y=top10['Att_Float'],
                text=[f"{v:.0%}" for v in top10['Att_Float']], textposition='auto',
                marker_color='#2ecc71'
            ))
            fig_p.update_layout(title='Highest Attendance Scores', margin=dict(t=30, b=0, l=0, r=0), height=220)
            fig_p.update_yaxes(tickformat='.0%')
            st.plotly_chart(fig_p, use_container_width=True)

        with pp2:
            st.dataframe(
                candidates[['Volunteer_ID','Full_Name','Neighborhood','Attendance_Rate','Skills']],
                use_container_width=True, hide_index=True, height=380
            )

        if len(candidates) > 0:
            if st.button("Draft Recognition Briefing", type="primary", key="promo_btn"):
                with st.spinner("Drafting briefing..."):
                    safe_p = candidates[['Volunteer_ID','Neighborhood','Skills','Attendance_Rate']].head(10)
                    ai_out = call_ai(f"""
Top performing volunteers (attendance ≥ {p_thresh}%):
{safe_p.to_csv(index=False)}

## RECOGNITION RECOMMENDATIONS
Highlight the top 3 IDs and how their specific skills make them incredibly valuable to our events.

## THANK YOU MESSAGE
Draft a warm, professional email thanking them for their outstanding attendance and continuous dedication.
""", "You are a volunteer engagement coordinator for an NGO.")
                st.info("Briefing Generated")
                st.markdown(ai_out)

# ════════════════════════════════════════════════════════════════════════════
#  05 · AI ASSISTANT
# ════════════════════════════════════════════════════════════════════════════
elif page == "AI Assistant":
    st.title("AI Assistant")
    st.write("Chat with an AI assistant that understands your workforce data overview. (No personal data is shared)")

    region_ctx = df.groupby('Neighborhood').agg(
        Headcount=('Volunteer_ID','count'),
        Avg_Att=('Att_Float','mean'),
    ).reset_index().to_csv(index=False)

    top_skills = pd.Series(parse_skills(df['Skills'])).value_counts().head(20).to_string()

    SYSTEM = f"""You are a helpful and professional NGO operations assistant.

DATA SNAPSHOT:
- Total Workforce: {len(df)} Volunteers
- Average Attendance: {avg_att:.0%} | Active Regions: {len(neighborhoods)}
- At-Risk Volunteers (<50%): {len(df[df['Att_Float']<0.50])}

REGIONAL DATA:
{region_ctx}

TOP SKILLS IN ROSTER:
{top_skills}

Please answer questions based on this data. Be concise, polite, and helpful. Never request or reveal personal data."""

    if "cop_msgs" not in st.session_state:
        st.session_state.cop_msgs =[]

    st.subheader("Suggested Questions")
    qcols = st.columns(4)
    quick_queries =[
        "Which region has the lowest attendance?",
        "Do we have enough medics for an event?",
        "What skills are most common?",
        "Give me a brief overview of our workforce.",
    ]
    for qcol, q in zip(qcols, quick_queries):
        if qcol.button(q, key=f"q_{q[:10]}", use_container_width=True):
            st.session_state.cop_msgs.append({"role":"user","content":q})
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"system","content":SYSTEM}] + st.session_state.cop_msgs,
                max_tokens=1024
            )
            ai = r.choices[0].message.content
            st.session_state.cop_msgs.append({"role":"assistant","content":ai})
            st.rerun()

    st.divider()

    for msg in st.session_state.cop_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.cop_msgs.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            msgs =[{"role":"system","content":SYSTEM}] + st.session_state.cop_msgs
            r    = client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=1024)
            ai   = r.choices[0].message.content
            st.markdown(ai)
            st.session_state.cop_msgs.append({"role":"assistant","content":ai})

    st.divider()
    d1, d2, d3 = st.columns([1,1,2])

    if d1.button("Clear Chat", key="clear_cop"):
        st.session_state.cop_msgs =[]
        st.rerun()

    if d2.button("Generate Status Report", type="primary", key="donor_rpt"):
        with st.spinner("Compiling report..."):
            ai_out = call_ai(f"""
Write a professional NGO Workforce Status Report.

DATA:
- Total Workforce: {len(df)} Volunteers across {len(neighborhoods)} neighborhoods
- Avg Attendance: {avg_att:.0%}
- Top Skills: {', '.join(pd.Series(parse_skills(df['Skills'])).value_counts().head(8).index.tolist())}

REGIONAL DATA:
{region_ctx}

Sections:
1. EXECUTIVE SUMMARY
2. WORKFORCE STRENGTH
3. REGIONAL REACH
4. FUTURE GOALS
""", "You are an NGO communications coordinator.")
        st.subheader("Workforce Status Report")
        st.markdown(ai_out)