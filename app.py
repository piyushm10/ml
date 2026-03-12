import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_pickle("patient_591.pkl")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

patient_id = "591"

pdf = df[df["patient_id"] == patient_id].copy()

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

date_colors = [
    "red","green","blue","orange","purple",
    "brown","pink","cyan","magenta","yellow"
]

pdf["glucose_level"] = pd.to_numeric(pdf["glucose_level"], errors="coerce")

for attr in continuous_attrs:
    pdf[attr] = pd.to_numeric(pdf[attr], errors="coerce")

unique_dates = sorted(pdf["timestamp"].dt.date.unique())

fig = go.Figure()

# Glucose trace
fig.add_trace(go.Scattergl(
    x=pdf["timestamp"],
    y=pdf["glucose_level"],
    mode="lines",
    connectgaps=True,
    line=dict(width=2, color="blue"),
    name="Glucose"
))

# Continuous attributes
for attr in continuous_attrs:
    fig.add_trace(go.Scattergl(
        x=pdf["timestamp"],
        y=pdf[attr],
        mode="lines",
        connectgaps=True,
        line=dict(width=2),
        name=attr,
        visible=False,
        yaxis="y2"
    ))

buttons = []

buttons.append(dict(
    label="None",
    method="update",
    args=[{"visible":[True]+[False]*len(continuous_attrs)}]
))

for i, attr in enumerate(continuous_attrs):

    vis = [True] + [False]*len(continuous_attrs)
    vis[i+1] = True

    buttons.append(dict(
        label=attr,
        method="update",
        args=[{"visible": vis}]
    ))

# Event markers
for event in event_attrs:

    events = pdf[pdf[event].notna()]

    xs = []
    ys = []
    labels = []
    colors = []

    for _, r in events.iterrows():

        date_index = unique_dates.index(r["timestamp"].date())
        color = date_colors[date_index % len(date_colors)]

        if event == "meal_type":
            label = f"{r['meal_type']} ({r['meal_carbs']}g)"
        elif event == "bolus_dose":
            label = f"bolus {r['bolus_dose']}"
        elif event == "exercise_intensity":
            label = f"exercise {r['exercise_intensity']}"
        elif event == "finger_stick":
            label = f"finger {r['finger_stick']}"
        elif event == "basal":
            label = f"basal {r['basal']}"
        elif event == "temp_basal":
            label = f"temp basal {r['temp_basal']}"
        elif event == "hypo_event":
            label = "hypo"
        else:
            label = event

        xs.append(r["timestamp"])
        ys.append(r["glucose_level"])
        labels.append(label)
        colors.append(color)

    fig.add_trace(go.Scattergl(
        x=xs,
        y=ys,
        mode="markers",
        marker=dict(size=8, color=colors),
        text=labels,
        hovertemplate="%{text}<extra></extra>",
        name=event,
        visible=False
    ))

date_buttons = []

for d in unique_dates:

    start = pd.Timestamp(d)
    end = start + pd.Timedelta(days=1)

    date_buttons.append(dict(
        label=str(d),
        method="relayout",
        args=[{"xaxis.range":[start,end]}]
    ))

fig.update_layout(

    title="Glucose vs Selected Attribute",

    xaxis=dict(
        title="Timestamp",
        type="date",

        rangeselector=dict(
            buttons=[
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(step="all")
            ]
        ),

        rangeslider=dict(visible=True)
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

    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.15,
            y=1
        ),
        dict(
            buttons=date_buttons,
            direction="down",
            showactive=True,
            x=0.35,
            y=1.15
        )
    ],

    template="plotly_white",
    height=650
)

st.plotly_chart(fig, use_container_width=True)
