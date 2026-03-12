import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("CGM Glucose Visualization (Patient 559)")

# -------------------------
# Load dataset
# -------------------------
df = pd.read_pickle("patient_559.pkl")
df["timestamp"] = pd.to_datetime(df["timestamp"])

pdf = df.copy()

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
# Colors
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

feature_colors = [
    "#ff7f0e","#2ca02c","#d62728","#9467bd",
    "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"
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

# ensure numeric
pdf["glucose_level"] = pd.to_numeric(pdf["glucose_level"], errors="coerce")

for attr in continuous_attrs:
    pdf[attr] = pd.to_numeric(pdf[attr], errors="coerce")

# -------------------------
# Plot
# -------------------------
fig = go.Figure()

# Glucose line
fig.add_trace(go.Scatter(
    x=pdf["timestamp"],
    y=pdf["glucose_level"],
    mode="lines",
    name="Glucose",
    line=dict(color="#1f77b4", width=3),
    connectgaps=True
))

# Continuous attributes
for i, attr in enumerate(selected_features):

    color = feature_colors[i % len(feature_colors)]

    fig.add_trace(go.Scatter(
        x=pdf["timestamp"],
        y=pdf[attr],
        mode="lines",
        name=attr,
        line=dict(color=color, width=2),
        yaxis="y2"
    ))

# -------------------------
# Event vertical lines
# -------------------------
shapes = []
annotations = []

for event in selected_events:

    events = pdf[pdf[event].notna()]

    for _, r in events.iterrows():

        shapes.append(dict(
            type="line",
            x0=r["timestamp"],
            x1=r["timestamp"],
            y0=0,
            y1=400,
            line=dict(
                color=event_colors[event],
                dash="dot",
                width=2
            )
        ))

        annotations.append(dict(
            x=r["timestamp"],
            y=0,
            text=event,
            showarrow=False,
            yshift=-12,
            font=dict(size=10, color=event_colors[event])
        ))

# Legend entries for events
for event, color in event_colors.items():
    if event in selected_events:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color=color, dash="dot", width=3),
            name=event
        ))

# -------------------------
# Layout
# -------------------------
fig.update_layout(

    title="Glucose Visualization",

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
    annotations=annotations,

    template="plotly_white",
    height=750
)

st.plotly_chart(fig, use_container_width=True)
