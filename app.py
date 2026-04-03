import streamlit as st
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="NGO AI Operations", page_icon="🏢", layout="wide")
st.title("🏢 NGO AI Operations Manager")

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.warning("Please configure your Groq API Key.")
    st.stop()

client = Groq(api_key=api_key)

# --- Upload Data Once ---
uploaded_file = st.file_uploader("Upload Complex Volunteer CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Full_Name'] = df['First_Name'] + " " + df['Last_Name']
    
    # Create Tabs for the two features
    tab1, tab2 = st.tabs(["🎯 Event Matchmaker", "🔍 Query Individual"])

    # ==========================================
    # TAB 1: THE EVENT MATCHMAKER
    # ==========================================
    with tab1:
        st.write("Plan an event, and the AI will find the best staff for it based on skills, vehicles, and attendance.")
        
        events_text = st.text_area(
            "What event are you planning?", 
            value="We are hosting a medical camp this Saturday. We need to move a lot of heavy boxes, we need someone with first aid skills, and we need someone who has a car to drive supplies.",
            height=100
        )

        if st.button("Generate Match & Decoder Ring", type="primary"):
            with st.spinner("Thinking..."):
                # Privacy: Send everything EXCEPT names/phones/emails
                ai_safe_df = df[['Volunteer_ID', 'Interests', 'Skills', 'Has_Vehicle', 'Attendance_Rate', 'Preferred_Days']]
                
                prompt = f"""
                You are the NGO Operations Manager. 
                Event request: {events_text}
                
                Here is our anonymized volunteer pool:
                {ai_safe_df.to_csv(index=False)}
                
                YOUR TASK:
                Select exactly 3-5 volunteers who are the BEST fit for this specific event. 
                Prioritize people with high attendance rates (>75%) and matching skills/vehicle status.
                
                Format:
                1. State the exact Volunteer_IDs chosen.
                2. Explain why they were chosen based on their specific stats.
                3. Draft a WhatsApp message to send to them.
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_text = response.choices[0].message.content
                st.markdown("### 🤖 AI Strategy")
                st.write(ai_text)
                
                # --- THE DECODER RING (Solving your headache) ---
                st.markdown("### 📞 Contact List (The Decoder)")
                # Python scans the AI text for anything matching "V-XXX"
                found_ids = list(set(re.findall(r'V-\d{3}', ai_text)))
                
                if found_ids:
                    # Filter the dataframe to only show the people the AI picked
                    contact_list = df[df['Volunteer_ID'].isin(found_ids)][['Volunteer_ID', 'Full_Name', 'Phone_Number', 'Skills']]
                    st.dataframe(contact_list, use_container_width=True)
                    st.success(f"👆 Here are the real names and numbers for the IDs the AI selected! Just copy the WhatsApp draft and text them.")
                else:
                    st.warning("No specific IDs were found in the AI response.")


    # ==========================================
    # TAB 2: INDIVIDUAL LOOKUP
    # ==========================================
    with tab2:
        st.write("Select a specific volunteer to generate a personalized action plan or check-in message.")
        
        selected_person = st.selectbox("Select a Volunteer:", df['Full_Name'])
        
        # Get their specific data
        person_data = df[df['Full_Name'] == selected_person].iloc[0]
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**Stats for {person_data['First_Name']}**\n"
                    f"- **Phone:** {person_data['Phone_Number']}\n"
                    f"- **Skills:** {person_data['Skills']}\n"
                    f"- **Attendance:** {person_data['Attendance_Rate']}\n"
                    f"- **Vehicle:** {person_data['Has_Vehicle']}")
            
            goal = st.text_input("What do you want to do with them?", value="Write a nice text thanking them for being so reliable, and ask if they are free next week.")
            
        with col_b:
            if st.button("Generate Message for " + person_data['First_Name']):
                with st.spinner("Writing..."):
                    # For a single person, we CAN pass their first name to the AI to make it sound human
                    single_prompt = f"""
                    You are an NGO Manager. 
                    I need to text a volunteer named {person_data['First_Name']}.
                    Their stats: They like {person_data['Interests']}, their skills are {person_data['Skills']}, and their past attendance is {person_data['Attendance_Rate']}.
                    
                    Goal of the message: {goal}
                    
                    Draft a highly personalized, warm WhatsApp message based on their stats. Keep it under 4 sentences.
                    """
                    
                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": single_prompt}]
                    )
                    st.write(res.choices[0].message.content)

else:
    st.info("Upload the new complex CSV to begin.")