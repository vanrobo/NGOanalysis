# 🎯 Quick Start Guide

## 1. Installation

```bash
pip install -r requirements.txt
```

## 2. Environment Setup

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key from: https://console.groq.com

## 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 4. Prepare Your Data

Your CSV should have these columns:

| Column            | Format                | Example                           |
| ----------------- | --------------------- | --------------------------------- |
| `Volunteer_ID`    | Text                  | V-001                             |
| `First_Name`      | Text                  | Aarav                             |
| `Last_Name`       | Text                  | Sharma                            |
| `Phone_Number`    | Text                  | +91-9876543210                    |
| `Email`           | Text                  | aarav@example.com                 |
| `Interests`       | Semicolon-separated   | Cricket;Teaching;Healthcare       |
| `Skills`          | Semicolon-separated   | First Aid;Public Speaking;Driving |
| `Has_Vehicle`     | Yes/No                | Yes                               |
| `Attendance_Rate` | Percentage            | 95%                               |
| `Preferred_Days`  | Weekdays/Weekends/Any | Weekends                          |

**Example CSV** (data.csv):

```
Volunteer_ID,First_Name,Last_Name,Phone_Number,Email,Interests,Skills,Has_Vehicle,Attendance_Rate,Preferred_Days
V-001,Aarav,Sharma,+91-9876543210,aarav.s@example.com,Cricket;Teaching,First Aid;Public Speaking,Yes,95%,Weekends
V-002,Priya,Patel,+91-9876543211,priya.p@example.com,Healthcare;Fundraising,Accounting;Social Media,No,60%,Weekdays
```

## 5. Using Each Tab

### 🎯 Event Matchmaker

1. Select "Event Matchmaker" tab
2. Describe your event needs (e.g., "Need 3 people for a medical camp, must have First Aid")
3. Click "Generate Plan & Contact List"
4. AI will suggest best volunteers with reasoning
5. Get contact information to reach out

### 👤 Volunteer Profile

1. Select a volunteer from dropdown
2. See complete profile information
3. Ask custom questions (e.g., "Create a thank you message")
4. Click button to get AI-generated response

### 🎓 Career Advisor

1. Select volunteer
2. Click "Generate Career Paths"
3. Get 3 personalized career recommendations
4. See required skills and industries for each path

### 🛣️ Skill Roadmap

1. Select volunteer
2. Enter your goal (e.g., "Become a project manager")
3. Click "Build My Learning Path"
4. Get 6-month structured learning plan
5. Includes resources, time commitment, projects

### 🤝 Mentorship Matcher

1. Select volunteer who wants mentoring
2. Describe learning goal (e.g., "Leadership and project management")
3. Click "Find My Mentor Match"
4. Get top 3 mentor suggestions with why they fit

### 📊 Impact Analyzer

1. Select volunteer
2. Click "Analyze My Impact Potential"
3. See impact scores across different NGO roles
4. Get top recommendation with 30-60-90 day plan
5. Discover scaling opportunities

---

## 💾 Troubleshooting

### "API Key Error"

- Check `.env` file exists in project root
- Verify API key from https://console.groq.com
- Key should start with `gsk_`

### "CSV Upload Failed"

- Ensure column names match exactly
- Check for special characters in data
- Verify semicolon separation for lists

### "Volunteer Not Found"

- Make sure Full_Name is correctly calculated (First_Name + Last_Name)
- Check for extra spaces in names

### "AI Response is Generic"

- Longer, more detailed interests/skills = better recommendations
- Try being more specific in your queries
- Examples: "Project management for healthcare nonprofits" instead of just "management"

---

## 🔐 Security Best Practices

1. **Don't commit `.env`** to git (add to .gitignore)
2. **API Key rotation**: Refresh keys regularly from Groq console
3. **Data handling**: CSV is processed locally, not stored
4. **Limit access**: Share app link only with authorized staff

---

## 📈 Tips for Best Results

1. **Rich profiles work better**
   - Add multiple interests per volunteer
   - List all relevant skills
   - Keep data updated

2. **Specific goals get better recommendations**
   - "Become a healthcare program coordinator" > "Get better"
   - "Leadership in crisis management" > "Leadership"

3. **Regular reviews**
   - Check career paths quarterly
   - Update skill roadmaps as they progress
   - Mentor matches may evolve over time

4. **Share insights**
   - Use AI recommendations in 1-on-1s with volunteers
   - Build development plans together
   - Track progress on roadmaps

---

## 📞 Support

For issues or feature requests, check:

- Groq API docs: https://console.groq.com/docs
- Streamlit docs: https://docs.streamlit.io
- This repo's FEATURES.md for detailed feature info
