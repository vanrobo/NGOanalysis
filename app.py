import streamlit as st
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="NGO AI Operations", page_icon="🏢", layout="wide")
st.title("🏢 NGO AI Operations Manager")

# Setup API Key
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.warning("Please configure your Groq API Key.")
    st.stop()

client = Groq(api_key=api_key)

# 1. Upload Data (This stays at the top)
uploaded_file = st.file_uploader("Upload Volunteer CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Combine names for easy lookup later
    df['Full_Name'] = df['First_Name'] + " " + df['Last_Name']
    
    # 2. CREATE THE TABS (This is the feature you are missing!)
    tab1, tab2 = st.tabs(["🎯 Event Matchmaker", "🔍 Query Individual"])

    # --- TAB 1: THE BRAIN ---
    with tab1:
        st.subheader("Plan your Events")
        events_text = st.text_area(
            "What events are you planning?", 
            value="We need 3 people for a medical camp this Saturday. Must have 'First Aid' skills and 'High Attendance'.",
            height=100
        )

        if st.button("Generate Plan & Contact List", type="primary"):
            with st.spinner("AI is matching volunteers..."):
                # Privacy: Remove names/phones for the AI
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
                
                # --- THE DECODER RING ---
                st.markdown("---")
                st.subheader("📞 Actionable Contact List")
                # This finds "V-001" etc in the AI's text
                found_ids = list(set(re.findall(r'V-\d{3}', ai_text)))
                
                if found_ids:
                    # Matches IDs back to real names and phone numbers
                    contacts = df[df['Volunteer_ID'].isin(found_ids)][['Volunteer_ID', 'Full_Name', 'Phone_Number', 'Skills']]
                    st.table(contacts)
                    st.success("The AI chose these people. Their real contact info is above!")

    # --- TAB 2: THE QUERY FEATURE ---
    with tab2:
        st.subheader("Look up a Specific Person")
        name_to_query = st.selectbox("Select a Volunteer:", df['Full_Name'].unique())
        
        person = df[df['Full_Name'] == name_to_query].iloc[0]
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write(f"**Current Data for {name_to_query}:**")
            st.json({
                "Phone": person['Phone_Number'],
                "Attendance": person['Attendance_Rate'],
                "Skills": person['Skills'],
                "Vehicle": person['Has_Vehicle']
            })
            
        with col_right:
            query_task = st.text_input("What do you want to do?", value="Write a 'Thank You' message for their great attendance.")
            if st.button(f"Generate Message for {person['First_Name']}"):
                q_prompt = f"Volunteer {person['First_Name']} has {person['Attendance_Rate']} attendance and skills: {person['Skills']}. Goal: {query_task}. Draft a 2-sentence WhatsApp."
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q_prompt}])
                st.success(res.choices[0].message.content)

else:
    st.info("Please upload your volunteer CSV to unlock the Matchmaker and Query tools.")