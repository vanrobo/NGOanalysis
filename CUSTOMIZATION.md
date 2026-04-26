# ⚙️ Customization Guide

## Adapting to Your NGO Type

### 1. Healthcare NGO

**Customize Career Paths**

```python
# In app.py, modify career_prompt:
career_paths = [
    "Healthcare Program Manager",
    "Community Health Worker",
    "Medical Social Worker",
    "Health Educator",
    "Hospital Administrator"
]
```

**Custom Skill Roadmap Topics**

```
- First Aid & CPR Certification
- Medical Ethics & Patient Communication
- Healthcare Data Management
- Epidemiology Basics
```

**Tailored Impact Metrics**

```
- People screened: X per month
- Lives impacted: X per month
- Prevention vs Treatment: ratio
- Health outcomes improved: %
```

---

### 2. Education NGO

**Custom Roles**

```
- Curriculum Developer
- Teaching Coach
- Education Program Manager
- Student Success Coordinator
- Educational Technology Specialist
```

**Custom Skill Focus**

```
- Pedagogy (how to teach)
- Curriculum Design
- Learning Assessment
- Educational Technology
- Mentoring Students
```

**Custom Metrics**

```
- Students taught/mentored
- Learning outcomes improved
- Schools/communities reached
- Educational hours delivered
```

---

### 3. Environmental NGO

**Custom Roles**

```
- Environmental Educator
- Project Coordinator
- Community Mobilizer
- Research Assistant
- Communications & Advocacy Lead
```

**Custom Skills**

```
- Environmental Science Basics
- Community Organizing
- Project Planning
- Data Collection & Analysis
- Advocacy & Communications
```

**Custom Impact**

```
- Trees planted
- Communities educated
- Policy changes influenced
- Waste reduced
- Emissions prevented
```

---

### 4. Social Justice NGO

**Custom Roles**

```
- Community Advocate
- Policy Analyst
- Communications Specialist
- Grant Writer
- Volunteer Coordinator
```

**Custom Skills**

```
- Community Organizing
- Policy Analysis
- Storytelling for Change
- Data Advocacy
- Grant Writing
```

**Custom Metrics**

```
- People advocated for
- Policy influencedchanges
- Community voice amplified
- Stories told
- Funding secured
```

---

## Feature Customization Examples

### Modify Event Matchmaker for Your Needs

**Current (Generic)**

```python
events_text = st.text_area(
    "What events are you planning?",
    value="We need 3 people for a medical camp this Saturday...",
)
```

**Customized for Education NGO**

```python
events_text = st.text_area(
    "What teaching opportunity are you planning?",
    value="Summer camp: Need 5 tutors for Math/Science/English. 50 students. 3 weeks.",
)
```

**Customized for Environment NGO**

```python
events_text = st.text_area(
    "What environmental initiative are you planning?",
    value="Tree planting drive: 1000 trees, need logistics + community coordination. 2 days.",
)
```

---

### Customize Career Advisor Prompts

**Current (Generic)**

```python
career_prompt = f"""
Volunteer Profile:
- Interests: {person['Interests']}
- Skills: {person['Skills']}

Suggest top 3 career paths...
"""
```

**For Education NGO**

```python
career_prompt = f"""
Educator Profile:
- Teaching Interests: {person['Interests']}
- Current Skills: {person['Skills']}
- Student Group Preference: {additional_prefs}

Suggest top 3 education career paths:
1. In NGO sector (impact focus)
2. In formal education (stability)
3. In EdTech (innovation)

For each path, include:
- Student demographics you'd work with
- Technology you'd use
- Impact on learning outcomes
"""
```

---

### Custom Skill Roadmaps by NGO Type

**Healthcare Focus**

```
6-MONTH PLAN FOR HEALTHCARE VOLUNTEER:
- Months 1-2: Healthcare Communication & Patient Empathy
- Months 3-4: Basic Clinical/Administrative Knowledge
- Months 5-6: Program Leadership & Team Management
```

**Education Focus**

```
6-MONTH PLAN FOR EDUCATION VOLUNTEER:
- Months 1-2: Pedagogy & Classroom Management
- Months 3-4: Curriculum Design & Student Assessment
- Months 5-6: Educational Leadership & Mentoring
```

**Environment Focus**

```
6-MONTH PLAN FOR ENVIRONMENTAL VOLUNTEER:
- Months 1-2: Environmental Science Basics & Community Organizing
- Months 3-4: Data Collection & Ecological Impact Measurement
- Months 5-6: Advocacy & Policy Communication
```

---

## Adding NGO-Specific Data Fields

### Option 1: Extend CSV Columns

**Before**

```
Volunteer_ID,First_Name,Last_Name,Interests,Skills,...
V-001,Aarav,Sharma,Teaching;Healthcare,First Aid;Public Speaking,...
```

**After (Healthcare NGO)**

```
Volunteer_ID,First_Name,...,Medical_Certifications,Patient_Interaction_Experience,Languages
V-001,Aarav,...,CPR;First Aid,Yes,English;Hindi;Spanish
```

**After (Education NGO)**

```
Volunteer_ID,First_Name,...,Grade_Preferences,Subjects,Teaching_Experience
V-001,Aarav,...,"6-8","Math;Science",Yes
```

### Option 2: Add Custom Selection in UI

```python
# Add to app after volunteer selection
if tab == "Custom Query":
    # For Healthcare NGO
    certifications = st.multiselect("Certifications:",
        ["First Aid", "CPR", "Blood Donation", "Other"])
    patient_type = st.radio("Experience with:",
        ["Children", "Elderly", "General Population"])
```

---

## Branding Customization

### Customize App Title & Colors

```python
# app.py
st.set_page_config(
    page_title="Education Impact Hub",  # Change this
    page_icon="📚",  # Change emoji
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Education Impact Hub")  # Change title
st.markdown("""
    <style>
    .main {
        background-color: #f0f7ff;  # Custom background
    }
    </style>
""", unsafe_allow_html=True)
```

### Customize Tab Emojis & Names

**Current**

```python
tab1, tab2, tab3 = st.tabs([
    "🎯 Event Matchmaker",
    "👤 Volunteer Profile",
    "🎓 Career Advisor",
    ...
])
```

**For Education NGO**

```python
tab1, tab2, tab3 = st.tabs([
    "📚 Class Coordinator",
    "👨‍🎓 Educator Profile",
    "🎯 Teaching Path Advisor",
    ...
])
```

**For Healthcare NGO**

```python
tab1, tab2, tab3 = st.tabs([
    "🏥 Medical Camp Coordinator",
    "👩‍⚕️ Healthcare Worker Profile",
    "💉 Medical Career Advisor",
    ...
])
```

---

## Advanced: Multi-Tenant Setup

### For Managing Multiple NGOs

```python
# app.py
ngo_list = ["Education NGO", "Healthcare NGO", "Environment NGO"]
selected_ngo = st.sidebar.selectbox("Select Organization:", ngo_list)

# Load NGO-specific config
config = load_ngo_config(selected_ngo)  # Custom function

# Use config in prompts
if selected_ngo == "Education NGO":
    roles = config['education_roles']
    metrics = config['education_metrics']
elif selected_ngo == "Healthcare NGO":
    roles = config['healthcare_roles']
    metrics = config['healthcare_metrics']
```

### Config File Example (config.json)

```json
{
  "Education NGO": {
    "roles": ["Teacher", "Curriculum Designer", "Student Mentor", ...],
    "metrics": ["Students Taught", "Learning Outcomes", ...],
    "skills_emphasis": ["Pedagogy", "Student Assessment", ...],
    "branding": {
      "title": "📚 Education Impact Hub",
      "primary_color": "#4A90E2"
    }
  },
  "Healthcare NGO": {
    "roles": ["Healthcare Worker", "Patient Advocate", ...],
    "metrics": ["People Helped", "Health Improved", ...],
    "skills_emphasis": ["Medical Knowledge", "Patient Communication", ...],
    "branding": {
      "title": "🏥 Health Impact Hub",
      "primary_color": "#E84C3D"
    }
  }
}
```

---

## Localization

### For Multiple Languages

```python
translations = {
    "en": {
        "title": "NGO Volunteer Growth Hub",
        "event_label": "What events are you planning?",
        ...
    },
    "hi": {
        "title": "NGO स्वयंसेवक विकास केंद्र",
        "event_label": "आप कौन से कार्यक्रम की योजना बना रहे हैं?",
        ...
    },
    "es": {
        "title": "Centro de Crecimiento de Voluntarios de ONG",
        "event_label": "¿Qué eventos estás planeando?",
        ...
    }
}

# In app
language = st.sidebar.selectbox("Language:", ["English", "Hindi", "Spanish"])
lang_code = {"English": "en", "Hindi": "hi", "Spanish": "es"}[language]
strings = translations[lang_code]

st.title(strings["title"])
```

---

## Performance Optimization by NGO Size

### Small NGO (< 50 volunteers)

```python
# All features, all default settings
cache_data = False  # Reload fresh each time
```

### Medium NGO (50-500 volunteers)

```python
# Enable caching for performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_volunteer_data(csv_file):
    return pd.read_csv(csv_file)
```

### Large NGO (> 500 volunteers)

```python
# Use database instead of CSV
import sqlite3

def load_volunteer_data(db_path):
    conn = sqlite3.connect(db_path)
    return pd.read_sql("SELECT * FROM volunteers", conn)

# Filter by department/region in UI
department = st.sidebar.selectbox("Department:", departments)
df = load_volunteer_data(db_path, department=department)
```

---

## Testing Your Customizations

### 1. Create Test CSV

```csv
Volunteer_ID,First_Name,Last_Name,Phone_Number,Email,Interests,Skills,Has_Vehicle,Attendance_Rate,Preferred_Days
V-TEST1,Test,User1,+1-2025551234,test1@example.com,Interest1;Interest2,Skill1;Skill2,Yes,100%,Weekends
V-TEST2,Test,User2,+1-2025551235,test2@example.com,Interest3;Interest4,Skill3;Skill4,No,50%,Weekdays
```

### 2. Run Locally

```bash
streamlit run app.py
```

### 3. Test Each Tab

- [ ] Event Matchmaker - creates valid matches
- [ ] Volunteer Profile - shows correct data
- [ ] Career Advisor - gives relevant paths
- [ ] Skill Roadmap - provides actionable plan
- [ ] Mentorship Matcher - suggests good pairs
- [ ] Impact Analyzer - shows realistic scores

---

## Deployment Considerations

### Self-Hosted

```bash
# Docker for self-hosting
docker build -t ngo-hub .
docker run -p 8501:8501 ngo-hub
```

### Cloud Hosting

```bash
# Streamlit Cloud
streamlit run app.py --logger.level=debug

# Or deploy to:
# - Heroku
# - AWS
# - Google Cloud
# - Azure
```

### Security for Production

```python
# Require authentication
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
name, authentication_status, username = authenticator.login()

if not authentication_status:
    st.stop()
```

---

## Monitoring & Analytics

### Track Usage

```python
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

# Track when features are used
logging.info(f"User accessed Career Advisor for volunteer {volunteer_id}")
logging.info(f"Mentorship Match created between {mentee} and {mentor}")
```

### Get Insights

```
Questions to track:
- How many volunteers use Career Advisor?
- Which career paths are most popular?
- How many mentorship pairs form?
- What's average skill roadmap completion?
- Which NGO roles have highest demand?
```

---

## Next Steps

1. **Choose your NGO type** from examples above
2. **Customize prompts** in app.py
3. **Add NGO-specific fields** to CSV
4. **Test with sample data**
5. **Deploy** to your team
6. **Gather feedback** and iterate
7. **Scale** to all volunteers

See [README.md](README.md) for full documentation.
