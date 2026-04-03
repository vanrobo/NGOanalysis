import streamlit as st
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

st.set_page_config(page_title="NGO Volunteer Hub", page_icon="🤝")
st.title("🤝 NGO Volunteer Analyzer")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

uploaded_file = st.file_uploader("Upload your volunteers.csv file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} volunteers.")

    if st.button("🧠 Analyze Data"):
        # Privacy: Only send necessary columns
        ai_safe_df = df[['Volunteer_ID', 'Birth_Month', 'Birth_Day', 'Interests']]
        csv_string = ai_safe_df.to_csv(index=False)
        today = datetime.date.today().strftime('%B %d, %Y')
        
        prompt = f"""
        Today is {today}. Analyze this anonymized volunteer data:
        
        {csv_string}
        
        1. List Volunteer_IDs with birthdays in the next 30 days.
        2. Count how many volunteers like 'Cricket'.
        3. Suggest a low-budget social event combining 'Cricket' and 'Teaching'.
        4. Draft an enthusiastic WhatsApp invite for the cricket fans.
        """
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        
        st.markdown("### 📊 AI Insights")
        st.write(response.choices[0].message.content)