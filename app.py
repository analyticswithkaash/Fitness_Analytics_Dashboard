
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
api_key = st.sidebar.text_input(
    "Enter Groq API Key",
    type="password"
)

if api_key:
    client = Groq(api_key=api_key)
# Page configuration
st.set_page_config(
    page_title="Fitness Analytics Dashboard",
    page_icon="💪",
    layout="wide"
)

# Load cleaned dataset
df = pd.read_csv("workout_clean.csv")

st.title("💪 Personal Fitness Analytics Dashboard")
st.write("Explore your workout plan and exercise variations.")

# Sidebar filter
st.sidebar.header("Workout Filters")

muscles = st.sidebar.multiselect(
    "Select Muscle Groups",
    options=sorted(df["Muscle_Group"].dropna().unique()),
    default=sorted(df["Muscle_Group"].dropna().unique())
)

filtered_df = df[df["Muscle_Group"].isin(muscles)]

# KPI Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Exercise Rows", len(filtered_df))

with col2:
    st.metric(
        "Muscle Groups",
        filtered_df["Muscle_Group"].nunique()
    )

with col3:
    st.metric(
        "Exercise Options",
        filtered_df[
            ["Day_1_Exercise", "Day_2_Exercise"]
        ].count().sum()
    )

st.divider()

# Interactive chart
st.subheader("Muscle-wise Exercise Distribution")

counts = (
    filtered_df["Muscle_Group"]
    .value_counts()
    .reset_index()
)
counts.columns = ["Muscle Group", "Exercises"]

fig = px.bar(
    counts,
    x="Muscle Group",
    y="Exercises",
    color="Muscle Group",
    text="Exercises",
    title="Exercise Distribution by Muscle Group"
)

st.plotly_chart(fig, use_container_width=True)

# Workout table
st.subheader("Workout Exercise Library")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Day comparison
st.subheader("Day 1 vs Day 2 Workout")

day = st.radio(
    "Choose Workout Day",
    ["Day 1", "Day 2"],
    horizontal=True
)

column = (
    "Day_1_Exercise"
    if day == "Day 1"
    else "Day_2_Exercise"
)

st.dataframe(
    filtered_df[
        ["Muscle_Group", "Target_Muscle", column]
    ],
    use_container_width=True,
    hide_index=True
)
st.divider()
st.header("🤖 AI Fitness Assistant")

question = st.text_input(
    "Ask anything about your workout plan"
)

if st.button("Ask AI"):
    if not api_key:
        st.warning("Please enter your Groq API key.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            workout_data = df.to_csv(index=False)

            with st.spinner("AI is analyzing your workout..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a fitness data analyst. "
                                "Answer questions using the supplied "
                                "workout dataset. Do not invent data. "
                                "Distinguish workout plans from actual "
                                "training progress."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Workout Dataset:\n{workout_data}\n\n"
                                f"Question: {question}"
                            )
                        }
                    ]
                )

            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error(f"AI request failed: {e}")
