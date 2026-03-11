import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("CGM Glucose Visualization")

df = pd.read_pickle("all_combined.pkl")

patient = st.selectbox(
    "Select Patient",
    sorted(df["patient_id"].unique())
)

pdf = df[df["patient_id"] == patient]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=pdf["timestamp"],
    y=pdf["glucose_level"],
    mode="lines",
    name="Glucose"
))

fig.update_layout(
    yaxis=dict(range=[0,400]),
    xaxis_title="Time",
    yaxis_title="Glucose"
)

st.plotly_chart(fig)
