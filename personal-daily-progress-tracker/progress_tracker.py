import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Set Seaborn style
sns.set_style("whitegrid")
sns.set_palette("deep")

# Custom CSS with larger font size
st.markdown("""
    <style>
    body {
        font-size: 18px;
        font-family: 'Arial', sans-serif;
    }
    .main {
        background-color: #e6f0fa;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: #ffffff;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 18px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e65b50;
    }
    .stForm {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #d1e8f5;
    }
    .stSlider .st-bx {
        background-color: #26a69a;
    }
    .stSelectbox, .stTextInput input, .stNumberInput input {
        background-color: #f0f7ff;
        border-radius: 8px;
        border: 1px solid #80deea;
        font-size: 18px;
        color: #1a1a1a;
    }
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #80deea;
        background-color: #f0f7ff;
        font-size: 18px;
        color: #1a1a1a;
    }
    .header {
        color: #0288d1;
        font-size: 3em;
        text-align: center;
        margin-bottom: 10px;
    }
    .subheader {
        color: #0277bd;
        font-size: 2em;
        margin-top: 10px;
    }
    .success {
        color: #2e7d32;
        font-weight: 600;
        font-size: 18px;
    }
    .stMarkdown, .stDataFrame, .stText, .stInfo, .stWarning {
        color: #1a1a1a;
        font-size: 18px;
    }
    .stDataFrame table {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 8px;
        color: #1a1a1a;
        font-size: 18px;
    }
    .sidebar .stMarkdown, .sidebar .stPlotlyChart, .sidebar .stImage {
        color: #1a1a1a;
        font-size: 18px;
    }
    .sidebar .st-emotion-cache-1wrcr25 {
        background-color: #f0f7ff;
    }
    .stExpander {
        border: 1px solid #d1e8f5;
        border-radius: 8px;
        background-color: #fafcff;
        font-size: 18px;
    }
    .stCheckbox label {
        font-size: 18px;
    }
    .delete-button {
        background-color: #d32f2f;
        color: #ffffff;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 16px;
    }
    .delete-button:hover {
        background-color: #b71c1c;
    }
    </style>
""", unsafe_allow_html=True)

# Validate HH:MM format
def validate_time_format(time_str):
    if not time_str:
        return False
    pattern = r"^\d+:[0-5]\d$"
    if not re.match(pattern, time_str):
        return False
    hours, minutes = map(int, time_str.split(":"))
    return hours >= 0 and 0 <= minutes <= 59


# Load or create main ProgressTracker worksheet
def load_or_create_sheet(client):
    try:
        sheet = client.open("ProgressTracker").worksheet("ProgressTracker")
        headers = [
    "Date", "Daily Goals", "Mood", "Sleep Hours", "Gym Visited", 
"GATE Classes Attended", "Projects Worked On", "Tasks Completed", 
"Notes", "Gym Time", "Study Hours"
]
        data = sheet.get_all_records(expected_headers=headers)
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame(columns=[
                "Date", "Daily Goals", "Mood", "Sleep Hours", "Gym Visited", 
                "GATE Classes Attended", "Projects Worked On", "Tasks Completed", 
                "Notes", "Gym Time", "Study Hours"
            ])
        else:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            column_mapping = {
                "Goals": "Daily Goals",
                "Sleep_Hours": "Sleep Hours",
                "Gym": "Gym Visited",
                "Completing_GATE_Classes": "GATE Classes Attended",
                "Any_Project_Made": "Projects Worked On",
                "Tasks_Completed": "Tasks Completed",
                "Amount of Time Spent in Gym": "Gym Time"
            }
            df = df.rename(columns=column_mapping)
            if "Gym Time" not in df.columns:
                df["Gym Time"] = ""
            if "Study Hours" not in df.columns:
                df["Study Hours"] = ""
    except gspread.exceptions.SpreadsheetNotFound:
        sheet = client.create("ProgressTracker")
        sheet.share('progresstrackerapp@progresstrackerapp-461208.iam.gserviceaccount.com', perm_type="user", role="writer")
        worksheet = sheet.add_worksheet(title="ProgressTracker", rows=100, cols=11)
        worksheet.append_row([
            "Date", "Daily Goals", "Mood", "Sleep Hours", "Gym Visited", 
            "GATE Classes Attended", "Projects Worked On", "Tasks Completed", 
            "Notes", "Gym Time", "Study Hours"
        ])
        df = pd.DataFrame(columns=[
            "Date", "Daily Goals", "Mood", "Sleep Hours", "Gym Visited", 
            "GATE Classes Attended", "Projects Worked On", "Tasks Completed", 
            "Notes", "Gym Time", "Study Hours"
        ])
    return df, sheet

# Load or create ToDoList worksheet
def load_or_create_todo_sheet(client):
    try:
        sheet = client.open("ProgressTracker")
        try:
            worksheet = sheet.worksheet("ToDoList")
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            if df.empty:
                df = pd.DataFrame(columns=["Date", "Task", "Status"])
            else:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="ToDoList", rows=100, cols=3)
            worksheet.append_row(["Date", "Task", "Status"])
            df = pd.DataFrame(columns=["Date", "Task", "Status"])
    except gspread.exceptions.SpreadsheetNotFound:
        sheet = client.create("ProgressTracker")
        sheet.share('progresstrackerapp@progresstrackerapp-461208.iam.gserviceaccount.com', perm_type="user", role="writer")
        worksheet = sheet.add_worksheet(title="ToDoList", rows=100, cols=3)
        worksheet.append_row(["Date", "Task", "Status"])
        df = pd.DataFrame(columns=["Date", "Task", "Status"])
    return df, worksheet

# Save main ProgressTracker data
def save_to_sheet(df, worksheet, new_entry=None):
    if new_entry is not None:
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = df['Date'].dt.strftime("%Y-%m-%d").fillna(df['Date'])
    worksheet.clear()
    worksheet.append_row([
        "Date", "Daily Goals", "Mood", "Sleep Hours", "Gym Visited", 
        "GATE Classes Attended", "Projects Worked On", "Tasks Completed", 
        "Notes", "Gym Time", "Study Hours"
    ])
    df = df.astype(str)
    worksheet.append_rows(df.values.tolist())
    return df

# Save To-Do List data
def save_todo_sheet(df, worksheet):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = df['Date'].dt.strftime("%Y-%m-%d").fillna(df['Date'])
    worksheet.clear()
    worksheet.append_row(["Date", "Task", "Status"])
    df = df.astype(str)
    worksheet.append_rows(df.values.tolist())
    return df

# Create visualizations
def create_visualizations(df):
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        mood_mapping = {"😊 Great": 5, "🙂 Good": 4, "😐 Neutral": 3, "😔 Low": 2, "😞 Very Low": 1}
        df['Mood_Value'] = df['Mood'].map(mood_mapping)
        
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.lineplot(data=df, x='Date', y='Mood_Value', marker='o', label='Mood', color='blue', ax=ax1)
        ax1.set_ylabel('Mood (1-5)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.set_ylim(1, 5)
        
        ax2 = ax1.twinx()
        sns.lineplot(data=df, x='Date', y='Sleep Hours', marker='s', label='Sleep Hours', color='green', ax=ax2)
        ax2.set_ylabel('Sleep Hours', color='green')
        ax2.tick_params(axis='y', labelcolor='green')
        
        ax1.set_title('Mood and Sleep Trends Over Time')
        fig1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        fig1.tight_layout()
        
        fig2, ax = plt.subplots(figsize=(6, 4))
        df_melted = df.melt(value_vars=['Gym Visited', 'GATE Classes Attended'], 
                           var_name='Activity', value_name='Status')
        sns.countplot(data=df_melted, x='Activity', hue='Status', ax=ax)
        ax.set_title('Gym Visits and GATE Classes Attended')
        ax.set_xlabel('Activity')
        ax.set_ylabel('Count')
        fig2.tight_layout()
        
        return fig1, fig2
    return None, None

# Initialize Google Sheets client
secrets = st.secrets["connections"]["gsheets"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    secrets, scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(credentials)

# Load data
progress_df, progress_sheet = load_or_create_sheet(client)
todo_df, todo_worksheet = load_or_create_todo_sheet(client)

# Streamlit app
st.markdown("<div class='header'>📊 Personal Daily Progress Tracker</div>", unsafe_allow_html=True)
st.markdown("Track your daily productivity, mood, gym, GATE classes, and projects from anywhere! 🚀", unsafe_allow_html=True)

# Sidebar: To-Do List and Visualizations
with st.sidebar:
    # To-Do List Section
    st.markdown("<div class='subheader'>📅 To-Do List Planner</div>", unsafe_allow_html=True)
    todo_date = st.date_input("Select Date for To-Do List", value=datetime.now(), key="todo_date")
    todo_tasks = st.text_area("Enter Tasks (one per line)", placeholder="e.g., Finish math homework\nAttend GATE class", height=100)
    
    if st.button("Add Tasks"):
        if todo_tasks:
            tasks = [task.strip() for task in todo_tasks.split("\n") if task.strip()]
            new_entries = [{"Date": todo_date, "Task": task, "Status": "Pending"} for task in tasks]
            todo_df = pd.concat([todo_df, pd.DataFrame(new_entries)], ignore_index=True)
            todo_df = save_todo_sheet(todo_df, todo_worksheet)
            st.success("Tasks added successfully!")
        else:
            st.warning("Please enter at least one task.")
    
    # Display tasks for selected date
    todo_date_str = todo_date.strftime("%Y-%m-%d")
    day_todos = todo_df[todo_df['Date'].astype(str) == todo_date_str]
    if not day_todos.empty:
        st.markdown(f"**Tasks for {todo_date_str}:**")
        for idx, row in day_todos.iterrows():
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"- {row['Task']} ({row['Status']})")
            with col2:
                if st.button("Delete", key=f"delete_todo_{idx}", help="Delete this task"):
                    todo_df = todo_df.drop(idx)
                    todo_df = save_todo_sheet(todo_df, todo_worksheet)
                    st.rerun()
    
    # Visualizations Section
    st.markdown("<div class='subheader'>📈 Progress Visualizations</div>", unsafe_allow_html=True)
    if not progress_df.empty:
        fig1, fig2 = create_visualizations(progress_df)
        if fig1 and fig2:
            st.pyplot(fig1)
            st.markdown("---")
            st.pyplot(fig2)
    else:
        st.info("No data available for visualization. Add entries to see trends!")

# Daily input form
with st.expander("📝 Add Today's Progress", expanded=True):
    with st.form(key="daily_tracker_form"):
        st.markdown("<div class='subheader'>Daily Progress Entry</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("📅 Date", value=datetime.now())
            daily_goals = st.text_area("🎯 Daily Goals", placeholder="What are your goals for today?", height=100)
            mood = st.selectbox("😊 Mood", ["😊 Great", "🙂 Good", "😐 Neutral", "😔 Low", "😞 Very Low"])
            sleep_hours = st.number_input("😴 Sleep Hours", min_value=0.0, max_value=24.0, step=0.5, value=8.0)
            study_hours_options = ["0:00", "0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "Custom"]
            study_hours_select = st.selectbox("📚 Study Hours (HH:MM)", study_hours_options)
            study_hours = study_hours_select
            if study_hours_select == "Custom":
                study_hours = st.text_input("Enter Custom Study Hours (HH:MM)", placeholder="e.g., 2:45")
        
        with col2:
            gym_visited = st.selectbox("🏋️ Gym Visited", ["Yes", "No"])
            gate_classes = st.selectbox("📚 GATE Classes Attended", ["Yes", "No"])
            projects_worked_on = st.text_area("🛠️ Projects Worked On", placeholder="Describe any project you worked on today", height=100)
            
            # Tasks Completed with Checkboxes
            st.markdown("✅ Tasks Completed")
            date_str = date.strftime("%Y-%m-%d")
            day_todos = todo_df[todo_df['Date'].astype(str) == date_str]
            completed_tasks = []
            if not day_todos.empty:
                for idx, row in day_todos.iterrows():
                    if st.checkbox(row['Task'], key=f"task_{idx}"):
                        completed_tasks.append(row['Task'])
                        todo_df.loc[idx, 'Status'] = "Completed"
            additional_tasks = st.text_area("Additional Completed Tasks", placeholder="Other tasks completed today", height=100)
        
        gym_time_options = ["0:00", "0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "Custom"]
        gym_time_select = st.selectbox("⏱️ Gym Time (HH:MM)", gym_time_options)
        gym_time = gym_time_select
        if gym_time_select == "Custom":
            gym_time = st.text_input("Enter Custom Gym Time (HH:MM)", placeholder="e.g., 1:45")
        
        notes = st.text_area("📓 Notes", placeholder="Any additional thoughts or reflections?", height=150)
        submit_button = st.form_submit_button("💾 Save Entry")

# Handle form submission
if submit_button:
    tasks_completed = ", ".join(completed_tasks)
    if additional_tasks:
        tasks_completed = tasks_completed + ", " + additional_tasks if tasks_completed else additional_tasks
    if not daily_goals or not projects_worked_on or not tasks_completed or not study_hours:
        st.warning("⚠️ Please fill in all required fields (Daily Goals, Projects Worked On, Tasks Completed, Study Hours).")
    elif not validate_time_format(study_hours):
        st.warning("⚠️ Please enter Study Hours in valid HH:MM format (e.g., 2:30, hours ≥ 0, minutes 0–59).")
    elif gym_time != "Custom" and validate_time_format(gym_time) or gym_time == "Custom" and validate_time_format(gym_time):
        new_entry = {
            "Date": date,
            "Daily Goals": daily_goals,
            "Mood": mood,
            "Sleep Hours": sleep_hours,
            "Gym Visited": gym_visited,
            "GATE Classes Attended": gate_classes,
            "Projects Worked On": projects_worked_on,
            "Tasks Completed": tasks_completed,
            "Notes": notes,
            "Gym Time": gym_time,
            "Study Hours": study_hours
        }
        progress_df = save_to_sheet(progress_df, progress_sheet, new_entry)
        todo_df = save_todo_sheet(todo_df, todo_worksheet)
        st.markdown("<div class='success'>🎉 Entry saved successfully!</div>", unsafe_allow_html=True)
        with st.expander("🔍 View Latest Entry"):
            st.write(new_entry)
    else:
        st.warning("⚠️ Please enter Gym Time in valid HH:MM format (e.g., 1:30, hours ≥ 0, minutes 0–59) or select a valid option.")

# Display recent entries with delete option and tabular view
if not progress_df.empty:
    
    # 📋 Tabular view (DataFrame styled)
    st.subheader("📊 Recent Progress Summary")
    styled_df = progress_df.tail(3).style.set_properties(**{
        'background-color': '#e3f2fd',
        'border-radius': '8px',
        'padding': '8px',
        'color': '#1a1a1a',
        'font-size': '16px'
    })
    st.dataframe(styled_df, use_container_width=True)

    # 📋 Detailed expandable view with delete option
    with st.expander("🧾 View & Manage Recent Entries", expanded=False):
        st.markdown("<div class='subheader'>Your Recent Progress</div>", unsafe_allow_html=True)
        recent_entries = progress_df.tail(3).reset_index()
        
        for idx, row in recent_entries.iterrows():
            with st.container():
                st.write(f"**Date**: {row['Date']}")
                st.write(f"**Daily Goals**: {row['Daily Goals']}")
                st.write(f"**Mood**: {row['Mood']}")
                st.write(f"**Sleep Hours**: {row['Sleep Hours']}")
                st.write(f"**Gym Visited**: {row['Gym Visited']}")
                st.write(f"**GATE Classes Attended**: {row['GATE Classes Attended']}")
                st.write(f"**Projects Worked On**: {row['Projects Worked On']}")
                st.write(f"**Tasks Completed**: {row['Tasks Completed']}")
                st.write(f"**Notes**: {row['Notes']}")
                st.write(f"**Gym Time**: {row['Gym Time']}")
                st.write(f"**Study Hours**: {row['Study Hours']}")
                
                if st.button("🗑️ Delete Entry", key=f"delete_entry_{row['index']}", help="Delete this entry"):
                    progress_df = progress_df.drop(row['index'])
                    progress_df = save_to_sheet(progress_df, progress_sheet)
                    st.success("Entry deleted.")
                    st.rerun()
                st.markdown("---")

else:
    st.info("No entries available.")

# Progress insights
with st.expander("📈 Progress Insights", expanded=False):
    st.markdown("<div class='subheader'>Your Progress Overview</div>", unsafe_allow_html=True)
    st.info("Check the sidebar for Mood, Sleep, Gym, and GATE Class trends! More insights coming soon. 🚀")