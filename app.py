import streamlit as st
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="NGO AI Coordinator", page_icon="🧠", layout="wide")
st.title("🧠 NGO AI Operations Manager")
st.write("Let the AI decide who to invite and what to say based on your calendar.")

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing Groq API Key.")
    st.stop()
client = Groq(api_key=api_key)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Your Data")
    uploaded_file = st.file_uploader("Upload Volunteer CSV", type="csv")
    
    st.subheader("2. Upcoming Events")
    events_text = st.text_area(
        "What events are you planning?", 
        value="1. Saturday: Beach Cleanup (Needs Logistics and Healthcare people)\n2. Next Wednesday: Slum Tutoring Drive (Needs Teaching and Art people)\n3. Next Sunday: Local Cricket Tournament Fundraiser (Needs Cricket and Event Planning people)",
        height=150
    )

with col2:
    st.subheader("3. AI Action Plan")
    if uploaded_file and st.button("Generate Strategy & Invites", type="primary"):
        with st.spinner("Analyzing calendar and cross-referencing volunteer skills..."):
            
            # Load and Anonymize Data
            df = pd.read_csv(uploaded_file)
            ai_safe_df = df[['Volunteer_ID', 'Interests']]
            volunteer_data = ai_safe_df.to_csv(index=False)
            
            # The Advanced Prompt
            prompt = f"""
            You are the Head Volunteer Coordinator for an NGO. 
            
            Here are the upcoming events we need to staff:
            {events_text}
            
            Here is our anonymized volunteer pool:
            {volunteer_data}
            
            YOUR TASK:
            For EVERY event listed, you must provide a detailed action plan. Do not give general advice. Be highly specific.
            
            Format your response exactly like this for each event:
            
            ### Event Name
            *   **Targeted Volunteer IDs:**[List the exact IDs of the people whose 'Interests' match the event needs. Don't list everyone, just the best matches.]
            *   **Why I chose them:**[Brief 1-sentence reasoning]
            *   **Actionable Next Step:**[What should the human NGO manager do next to secure these people?]
            *   **Draft WhatsApp Invite:**[Write a highly engaging, persuasive message to send to this specific group. Include placeholders for [Name].]
            
            ---
            """
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a brilliant, highly organized NGO Operations Manager."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")