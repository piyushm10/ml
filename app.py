import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("CGM Glucose Visualization")

# -------------------------
# Load dataset
# -------------------------
df = pd.read_pickle("patient_563.pkl")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# -------------------------
# Patient dropdown
# -------------------------
patients = sorted(df["patient_id"].unique())
patient_id = st.selectbox("Select Patient", patients)

pdf = df[df["patient_id"] == patient_id].copy()

# -------------------------
# Date selector
# -------------------------
available_dates = sorted(pdf["timestamp"].dt.date.unique())
selected_date = st.selectbox("Select Date", available_dates)

pdf = pdf[pdf["timestamp"].dt.date == selected_date]

# -------------------------
# Feature lists
# -------------------------
continuous_attrs = [
    "basis_heart_rate",
    "basis_steps",
    "basis_gsr",
    "basis_skin_temperature",
    "basis_air_temperature",
    "basis_sleep_quality"
]

event_attrs = [
    "meal_type",
    "exercise_intensity",
    "hypo_event",
    "finger_stick",
    "bolus_dose",
    "basal",
    "temp_basal"
]

# -------------------------
# Event colors
# -------------------------
event_colors = {
    "meal_type": "red",
    "exercise_intensity": "green",
    "hypo_event": "purple",
    "finger_stick": "orange",
    "bolus_dose": "blue",
    "basal": "brown",
    "temp_basal": "pink"
}

# -------------------------
# Feature selection
# -------------------------
selected_features = st.multiselect(
    "Select Continuous Features",
    continuous_attrs
)

selected_events = st.multiselect(
    "Select Event Markers",
    event_attrs
)

# ensure numeric columns
pdf["glucose_level"] = pd.to_numeric(pdf["glucose_level"], errors="coerce")

for attr in continuous_attrs:
    pdf[attr] = pd.to_numeric(pdf[attr], errors="coerce")

# -------------------------
# Color palette for features
# -------------------------
feature_colors = [
    "#1f77b4","#ff7f0e","#2ca02c","#d62728",
    "#9467bd","#8c564b","#e377c2","#7f7f7f",
    "#bcbd22","#17becf"
]

# -------------------------
# Plot
# -------------------------
fig = go.Figure()

# Glucose trace
fig.add_trace(go.Scatter(
    x=pdf["timestamp"],
    y=pdf["glucose_level"],
    mode="lines+markers",
    name="Glucose",
    line=dict(width=3, color="black"),
    marker=dict(size=4),
    yaxis="y1"
))

# Continuous attributes
for i, attr in enumerate(selected_features):

    color = feature_colors[i % len(feature_colors)]

    fig.add_trace(go.Scatter(
        x=pdf["timestamp"],
        y=pdf[attr],
        mode="lines+markers",
        name=attr,
        line=dict(width=2, color=color),
        marker=dict(size=4, color=color),
        yaxis="y2"
    ))

# -------------------------
# Event markers
# -------------------------
shapes = []

for event in selected_events:

    events = pdf[pdf[event].notna()]

    for _, r in events.iterrows():

        shapes.append(dict(
            type="line",
            x0=r["timestamp"],
            x1=r["timestamp"],
            y0=0,
            y1=r["glucose_level"],
            line=dict(
                color=event_colors[event],
                dash="dot",
                width=2
            )
        ))

# -------------------------
# Layout
# -------------------------
fig.update_layout(

    title=f"Glucose Visualization (Patient {patient_id})",

    xaxis=dict(
        title="Timestamp",
        type="date"
    ),

    yaxis=dict(
        title="Glucose (mg/dL)",
        range=[0,400]
    ),

    yaxis2=dict(
        title="Attribute Value",
        overlaying="y",
        side="right",
        showgrid=False
    ),

    shapes=shapes,
    template="plotly_white",
    height=700
)

st.plotly_chart(fig, use_container_width=True)
