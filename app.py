import pandas as pd
import plotly.graph_objects as go

patient_id = "591"

pdf = df[df["patient_id"] == patient_id].copy()
pdf["timestamp"] = pd.to_datetime(pdf["timestamp"])

# -------------------------
# Date selector
# -------------------------
unique_dates = sorted(pdf["timestamp"].dt.date.unique())

selected_date = unique_dates[0]   # default date

start = pd.Timestamp(selected_date)
end = start + pd.Timedelta(days=1)

# -------------------------
# Attributes
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

event_colors = {
    "meal_type":"red",
    "exercise_intensity":"green",
    "hypo_event":"purple",
    "finger_stick":"orange",
    "bolus_dose":"blue",
    "basal":"brown",
    "temp_basal":"pink"
}

# ensure numeric
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
    mode="lines",
    connectgaps=True,
    line=dict(width=3,color="#1f77b4"),
    name="Glucose",
    yaxis="y1"
))

# Continuous attributes
for attr in continuous_attrs:
    fig.add_trace(go.Scatter(
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

# NONE option
buttons.append(dict(
    label="None",
    method="update",
    args=[{"visible":[True]+[False]*len(continuous_attrs)}, {"shapes": [],"annotations":[]}]
))

# Continuous dropdown
for i, attr in enumerate(continuous_attrs):

    vis = [True] + [False]*len(continuous_attrs)
    vis[i+1] = True

    buttons.append(dict(
        label=attr,
        method="update",
        args=[{"visible": vis}, {"shapes": [],"annotations":[]}]
    ))

# Event dropdown
for event in event_attrs:

    shapes = []
    annotations = []

    events = pdf[pdf[event].notna()]

    for _, r in events.iterrows():

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

        shapes.append(dict(
            type="line",
            x0=r["timestamp"],
            x1=r["timestamp"],
            y0=0,
            y1=r["glucose_level"],
            line=dict(color=event_colors[event], dash="dot", width=2)
        ))

        annotations.append(dict(
            x=r["timestamp"],
            y=0,
            text=label,
            showarrow=False,
            textangle=90,
            yshift=-10,
            font=dict(size=10,color=event_colors[event])
        ))

    buttons.append(dict(
        label=event,
        method="update",
        args=[{"visible":[True]+[False]*len(continuous_attrs)}, {"shapes": shapes,"annotations":annotations}]
    ))

# Date dropdown
date_buttons = []

for d in unique_dates:

    start = pd.Timestamp(d)
    end = start + pd.Timedelta(days=1)

    date_buttons.append(dict(
        label=str(d),
        method="relayout",
        args=[{"xaxis.range":[start,end]}]
    ))

# -------------------------
# Layout
# -------------------------
fig.update_layout(

    title="Glucose vs Selected Attribute",

    xaxis=dict(
        title="Timestamp",
        type="date",
        range=[start,end],

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

fig.show()
