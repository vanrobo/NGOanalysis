import streamlit as st
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv
import json

load_dotenv()

st.set_page_config(page_title="NGO AI Operations & Volunteer Growth", page_icon="🏢", layout="wide")
st.title("🏢 NGO AI Operations & Volunteer Growth Hub")

# Setup API Key
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.warning("Please configure your Groq API Key.")
    st.stop()

client = Groq(api_key=api_key)

uploaded_file = st.file_uploader("Upload Volunteer CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Full_Name'] = df['First_Name'] + " " + df['Last_Name']
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Event Matchmaker", 
        "👤 Volunteer Profile", 
        "🎓 Career Advisor",
        "🛣️ Skill Roadmap",
        "🤝 Mentorship Matcher",
        "📊 Impact Analyzer"
    ])

    # ============ TAB 1: EVENT MATCHMAKER ============
    with tab1:
        st.subheader("🎯 Plan your Events")
        events_text = st.text_area(
            "What events are you planning?", 
            value="We need 3 people for a medical camp this Saturday. Must have 'First Aid' skills and 'High Attendance'.",
            height=100
        )

        if st.button("Generate Plan & Contact List", type="primary", key="event_match"):
            with st.spinner("AI is matching volunteers..."):
                ai_safe_df = df[['Volunteer_ID', 'Interests', 'Skills', 'Has_Vehicle', 'Attendance_Rate']]
                
                prompt = f"Events: {events_text}\n\nData:\n{ai_safe_df.to_csv(index=False)}\n\n" \
                         "Task: Pick 3 best volunteers. List their Volunteer_IDs clearly (e.g. V-001). " \
                         "Explain why and draft a WhatsApp message."
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_text = response.choices[0].message.content
                st.markdown(ai_text)
                
                st.markdown("---")
                st.subheader("📞 Actionable Contact List")
                found_ids = list(set(re.findall(r'V-\d{3}', ai_text)))
                
                if found_ids:
                    contacts = df[df['Volunteer_ID'].isin(found_ids)][['Volunteer_ID', 'Full_Name', 'Phone_Number', 'Skills']]
                    st.table(contacts)
                    st.success("The AI chose these people. Their real contact info is above!")

    # ============ TAB 2: VOLUNTEER PROFILE & QUERY ============
    with tab2:
        st.subheader("👤 Volunteer Profile & Query")
        name_to_query = st.selectbox("Select a Volunteer:", df['Full_Name'].unique(), key="profile_select")
        
        person = df[df['Full_Name'] == name_to_query].iloc[0]
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write(f"**📋 Profile for {name_to_query}:**")
            st.json({
                "ID": person['Volunteer_ID'],
                "Phone": person['Phone_Number'],
                "Email": person['Email'],
                "Interests": person['Interests'],
                "Skills": person['Skills'],
                "Attendance": person['Attendance_Rate'],
                "Has Vehicle": person['Has_Vehicle'],
                "Prefers": person['Preferred_Days']
            })
            
        with col_right:
            query_task = st.text_input("Custom Query:", value="Write a 'Thank You' message for their great attendance.", key="query_input")
            if st.button(f"AI Assist for {person['First_Name']}", key="query_btn"):
                q_prompt = f"Volunteer {person['First_Name']} has {person['Attendance_Rate']} attendance, interests: {person['Interests']}, and skills: {person['Skills']}. Goal: {query_task}. Provide thoughtful response."
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q_prompt}])
                st.success(res.choices[0].message.content)

    # ============ TAB 3: CAREER ADVISOR ============
    with tab3:
        st.subheader("🎓 Career Path Advisor")
        st.write("Get personalized career recommendations based on your skills and interests")
        
        career_volunteer = st.selectbox("Select Volunteer for Career Advice:", df['Full_Name'].unique(), key="career_select")
        
        if career_volunteer:
            person = df[df['Full_Name'] == career_volunteer].iloc[0]
            
            if st.button("🚀 Generate Career Paths", key="career_btn"):
                with st.spinner("AI analyzing career opportunities..."):
                    career_prompt = f"""
                    Volunteer Profile:
                    - Name: {person['First_Name']}
                    - Interests: {person['Interests']}
                    - Current Skills: {person['Skills']}
                    - Availability: {person['Preferred_Days']}
                    
                    Task: As a career advisor, analyze this volunteer's profile and suggest:
                    1. Top 3 career paths that match their interests and skills
                    2. For each career, explain why it fits and what makes them suitable
                    3. Specific job roles they could target (with realistic salary ranges if possible)
                    4. Skills they already have that are valuable
                    5. 2-3 new skills to develop for each path
                    6. Industries or organizations that would value their profile
                    
                    Provide practical, actionable career guidance focused on their specific interests and skills.
                    """
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": career_prompt}]
                    )
                    
                    st.success(response.choices[0].message.content)

    # ============ TAB 4: SKILL DEVELOPMENT ROADMAP ============
    with tab4:
        st.subheader("🛣️ Personalized Skill Development Roadmap")
        st.write("AI-generated learning path tailored to your goals and current skills")
        
        roadmap_volunteer = st.selectbox("Select Volunteer for Skill Roadmap:", df['Full_Name'].unique(), key="roadmap_select")
        goal = st.text_input("What's your career/skill goal?", value="Become a project manager in NGO sector", key="goal_input")
        
        if roadmap_volunteer and st.button("📚 Build My Learning Path", key="roadmap_btn"):
            with st.spinner("Creating personalized learning roadmap..."):
                person = df[df['Full_Name'] == roadmap_volunteer].iloc[0]
                
                roadmap_prompt = f"""
                Volunteer: {person['First_Name']}
                Current Skills: {person['Skills']}
                Current Interests: {person['Interests']}
                Goal: {goal}
                
                Create a detailed, 6-month skill development roadmap with:
                1. Current skill assessment (strengths and gaps)
                2. Month-by-month learning plan with specific skills/topics
                3. Recommended online resources (Coursera, Udemy, YouTube, etc.)
                4. Estimated time commitment per week
                5. Projects or volunteer activities to practice new skills
                6. Milestone checkpoints to track progress
                7. How this learning path connects to their goal
                8. Success metrics to measure improvement
                
                Make it practical, achievable, and inspiring!
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": roadmap_prompt}]
                )
                
                st.success(response.choices[0].message.content)

    # ============ TAB 5: MENTORSHIP MATCHER ============
    with tab5:
        st.subheader("🤝 Smart Mentorship Matcher")
        st.write("Connect volunteers with ideal mentors based on shared interests and complementary skills")
        
        mentee = st.selectbox("I want mentorship in:", df['Full_Name'].unique(), key="mentee_select")
        mentor_interest = st.text_input("What do you want to learn/improve?", value="Leadership and project management", key="mentor_topic")
        
        if mentee and st.button("🎯 Find My Mentor Match", key="mentor_btn"):
            with st.spinner("Matching mentors..."):
                person_mentee = df[df['Full_Name'] == mentee].iloc[0]
                
                # Create a version of df without the selected person
                other_volunteers = df[df['Volunteer_ID'] != person_mentee['Volunteer_ID']]
                
                mentor_prompt = f"""
                Mentee Profile:
                - Name: {person_mentee['First_Name']}
                - Interests: {person_mentee['Interests']}
                - Current Skills: {person_mentee['Skills']}
                - Learning Goal: {mentor_interest}
                
                Available Volunteers as Potential Mentors:
                {other_volunteers[['Volunteer_ID', 'First_Name', 'Skills', 'Interests']].to_csv(index=False)}
                
                Task: Identify the top 3 mentor matches and for each:
                1. Explain why they're a great mentor for this person
                2. What expertise they bring
                3. How their skills/interests align with the learning goal
                4. Suggested mentorship focus areas
                5. Recommended meeting frequency and format
                6. Sample first conversation starter
                
                Focus on creating meaningful mentoring relationships that benefit both people!
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": mentor_prompt}]
                )
                
                st.success(response.choices[0].message.content)

    # ============ TAB 6: IMPACT ANALYZER ============
    with tab6:
        st.subheader("📊 Impact & Role Analyzer")
        st.write("Discover roles in NGOs/nonprofits where you'd have the most impact")
        
        impact_volunteer = st.selectbox("Select Volunteer for Impact Analysis:", df['Full_Name'].unique(), key="impact_select")
        
        if impact_volunteer and st.button("💡 Analyze My Impact Potential", key="impact_btn"):
            with st.spinner("Calculating impact potential..."):
                person = df[df['Full_Name'] == impact_volunteer].iloc[0]
                
                impact_prompt = f"""
                Volunteer Profile:
                - Name: {person['First_Name']}
                - Skills: {person['Skills']}
                - Interests: {person['Interests']}
                - Availability: {person['Preferred_Days']}
                - Attendance Rate: {person['Attendance_Rate']}
                - Has Vehicle: {person['Has_Vehicle']}
                
                Analyze and provide:
                
                1. IMPACT SCORE for different NGO roles (0-100):
                   - Field Worker (healthcare/education)
                   - Program Coordinator
                   - Fundraiser
                   - Communications/Social Media Manager
                   - Logistics/Supply Chain
                   - Finance/Accounting
                   - Mentor/Trainer
                   
                2. For each role:
                   - Why this matches their profile
                   - Potential impact they could have
                   - People helped per month estimate
                   - How their skills make a difference
                   - What additional training needed
                   
                3. TOP RECOMMENDATION:
                   - Best role for maximum impact
                   - Detailed job description
                   - 30-60-90 day action plan
                   - Success metrics
                   
                4. SCALING OPPORTUNITY:
                   - How this person could multiply their impact
                   - Team building potential
                   - Leadership opportunities
                
                Make it inspiring and quantifiable!
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": impact_prompt}]
                )
                
                st.success(response.choices[0].message.content)

else:
    st.info("📤 Please upload your volunteer CSV to unlock all features!")
    st.write("""
    ### Expected CSV Columns:
    - Volunteer_ID, First_Name, Last_Name, Phone_Number, Email
    - Interests (semicolon-separated)
    - Skills (semicolon-separated)
    - Has_Vehicle, Attendance_Rate, Preferred_Days
    """)