import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("CGM Glucose Visualization")

# load dataset
df = pd.read_pickle("all_combined.pkl")

df["timestamp"] = pd.to_datetime(df["timestamp"])

# -------------------------
# Patient dropdown
# -------------------------
patients = sorted(df["patient_id"].unique())

patient_id = st.selectbox(
    "Select Patient",
    patients
)

pdf = df[df["patient_id"] == patient_id].copy()

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
# Plot
# -------------------------
fig = go.Figure()

# Glucose trace
fig.add_trace(go.Scatter(
    x=pdf["timestamp"],
    y=pdf["glucose_level"],
    mode="lines+markers",
    connectgaps=True,
    line=dict(width=2),
    marker=dict(size=4),
    name="Glucose",
    yaxis="y1"
))

# Selected continuous attributes
for attr in selected_features:
    fig.add_trace(go.Scatter(
        x=pdf["timestamp"],
        y=pdf[attr],
        mode="lines+markers",
        connectgaps=True,
        line=dict(width=2),
        marker=dict(size=4),
        name=attr,
        yaxis="y2"
    ))

# Event markers
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
            line=dict(color="red", dash="dot", width=2)
        ))

# -------------------------
# Layout
# -------------------------
fig.update_layout(

    title=f"Glucose Visualization (Patient {patient_id})",

    xaxis=dict(
        title="Timestamp",
        type="date",
        rangeslider=dict(visible=True),
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(step="all")
            ]
        )
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
    height=650
)

st.plotly_chart(fig, use_container_width=True)
