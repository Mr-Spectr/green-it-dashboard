"""Local Green IT dashboard for calculating data-center PUE and DCiE."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Green IT | PUE Dashboard", page_icon="🌱", layout="wide")


def calculate_metrics(facility_kwh: float, it_kwh: float) -> dict[str, float]:
    """Return the core energy-efficiency metrics for a valid measurement period."""
    non_it_kwh = facility_kwh - it_kwh
    pue = facility_kwh / it_kwh
    dcie = (it_kwh / facility_kwh) * 100
    return {"facility": facility_kwh, "it": it_kwh, "non_it": non_it_kwh, "pue": pue, "dcie": dcie}


def recommendation(pue: float) -> tuple[str, str]:
    if pue <= 1.20:
        return "Excellent efficiency", "Keep monitoring cooling and power distribution to preserve this low overhead."
    if pue <= 1.50:
        return "Good efficiency", "Review cooling schedules and airflow containment for the next practical improvement."
    if pue <= 2.00:
        return "Improvement opportunity", "Non-IT systems use a significant share of energy. Audit cooling, UPS losses, and lighting."
    return "High overhead", "Prioritize a facility energy audit. Cooling and power-delivery losses likely need attention."


def build_monitoring_data(facility_kwh: float, it_kwh: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create a repeatable seven-day monitoring sample scaled to the entered measurement."""
    daily_scale = facility_kwh / 30
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    daily_factor = [1.02, 1.05, 1.01, 1.04, 1.00, 0.91, 0.88]
    trend = pd.DataFrame({
        "Day": days,
        "Facility energy (kWh)": [daily_scale * f for f in daily_factor],
        "IT energy (kWh)": [(it_kwh / 30) * f for f in daily_factor],
    })
    trend["PUE"] = trend["Facility energy (kWh)"] / trend["IT energy (kWh)"]

    hours = list(range(24))
    profile = [0.76, 0.73, 0.71, 0.70, 0.71, 0.75, 0.84, 0.94, 1.02, 1.07, 1.10, 1.11,
               1.12, 1.10, 1.08, 1.06, 1.04, 1.08, 1.12, 1.09, 1.00, 0.91, 0.84, 0.79]
    heatmap = pd.DataFrame(
        [[daily_scale * factor * profile[hour] / 24 for hour in hours] for factor in daily_factor],
        index=days, columns=hours,
    )
    cooling = pd.DataFrame({
        "Supply air temperature (°C)": [18, 19, 20, 21, 22, 23, 24, 25],
        "Cooling overhead (kWh)": [facility_kwh - it_kwh + delta for delta in [120, 85, 50, 30, 15, 5, 25, 65]],
    })
    cooling["Cooling overhead (kWh)"] = cooling["Cooling overhead (kWh)"].clip(lower=0)
    cooling["Estimated PUE"] = (it_kwh + cooling["Cooling overhead (kWh)"]) / it_kwh
    return trend, heatmap, cooling


st.title("🌱 Green IT: Data Center Efficiency")
st.caption("Measure Power Usage Effectiveness (PUE), isolate non-IT overhead, and compare improvement scenarios.")

with st.sidebar:
    st.header("Your measurement")
    with st.form("energy_input"):
        timeframe = st.selectbox("Measurement period", ["Monthly", "Quarterly", "Annual"], index=0)
        facility_kwh = st.number_input("Total facility energy (kWh)", min_value=0.1, value=1000.0, step=50.0)
        it_kwh = st.number_input("IT equipment energy (kWh)", min_value=0.1, value=600.0, step=50.0)
        electricity_rate = st.number_input("Electricity rate (per kWh)", min_value=0.0, value=8.0, step=0.5, format="%.2f")
        carbon_factor = st.number_input("Grid carbon factor (kg CO₂e per kWh)", min_value=0.0, value=0.70, step=0.05, format="%.2f")
        submitted = st.form_submit_button("Calculate efficiency", type="primary", use_container_width=True)
    st.caption("Enter values for one consistent measurement period. IT energy covers servers, storage, and network equipment.")

if it_kwh > facility_kwh:
    st.error("IT equipment energy cannot exceed total facility energy. Adjust the values in the sidebar.")
    st.stop()

metrics = calculate_metrics(facility_kwh, it_kwh)
status, action = recommendation(metrics["pue"])

st.subheader(f"{timeframe} efficiency snapshot")
col1, col2, col3, col4 = st.columns(4)
col1.metric("PUE", f"{metrics['pue']:.2f}", help="Total facility energy divided by IT equipment energy.")
col2.metric("DCiE", f"{metrics['dcie']:.1f}%", help="IT equipment energy as a percentage of total facility energy.")
col3.metric("Non-IT overhead", f"{metrics['non_it']:,.0f} kWh")
col4.metric("IT share", f"{(metrics['it'] / metrics['facility']) * 100:.1f}%")

st.info(f"**{status}:** {action}")

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Energy breakdown")
    breakdown = pd.DataFrame({"Category": ["IT equipment", "Non-IT overhead"], "Energy (kWh)": [metrics["it"], metrics["non_it"]]})
    chart = px.pie(breakdown, names="Category", values="Energy (kWh)", hole=0.55,
                   color="Category", color_discrete_map={"IT equipment": "#16a34a", "Non-IT overhead": "#f59e0b"})
    chart.update_layout(margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
    st.plotly_chart(chart, use_container_width=True)

with right:
    st.subheader("Scenario comparison")
    default_rows = pd.DataFrame(
        {"Scenario": ["Legacy", "Baseline", "Optimized"], "IT energy (kWh)": [600.0, 600.0, 600.0], "Non-IT energy (kWh)": [400.0, 300.0, 150.0]}
    )
    scenarios = st.data_editor(default_rows, num_rows="dynamic", use_container_width=True, key="scenario_editor")
    scenarios["Total energy (kWh)"] = scenarios["IT energy (kWh)"] + scenarios["Non-IT energy (kWh)"]
    scenarios["PUE"] = scenarios["Total energy (kWh)"] / scenarios["IT energy (kWh)"].replace(0, float("nan"))
    scenario_chart = px.bar(scenarios, x="Scenario", y=["IT energy (kWh)", "Non-IT energy (kWh)"], barmode="stack",
                            color_discrete_sequence=["#16a34a", "#f59e0b"], labels={"value": "Energy (kWh)", "variable": "Source"})
    scenario_chart.update_layout(margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
    st.plotly_chart(scenario_chart, use_container_width=True)
    st.dataframe(scenarios[["Scenario", "Total energy (kWh)", "PUE"]].style.format({"Total energy (kWh)": "{:,.0f}", "PUE": "{:.2f}"}), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Operations monitoring")
trend, heatmap, cooling = build_monitoring_data(metrics["facility"], metrics["it"])
monitor_left, monitor_center, monitor_right = st.columns([0.85, 1.35, 1.2])
with monitor_left:
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=metrics["pue"], number={"valueformat": ".2f"}, title={"text": "Current PUE"},
        gauge={"axis": {"range": [1, 2.5]}, "bar": {"color": "#16a34a"},
               "steps": [{"range": [1, 1.5], "color": "#dcfce7"}, {"range": [1.5, 2], "color": "#fef3c7"}, {"range": [2, 2.5], "color": "#fee2e2"}],
               "threshold": {"line": {"color": "#dc2626", "width": 4}, "thickness": 0.8, "value": 2.0}}))
    gauge.update_layout(height=255, margin=dict(l=10, r=10, t=45, b=5))
    st.plotly_chart(gauge, use_container_width=True)

with monitor_center:
    st.caption("Seven-day energy trend")
    trend_chart = go.Figure()
    trend_chart.add_trace(go.Scatter(x=trend["Day"], y=trend["Facility energy (kWh)"], name="Facility energy", mode="lines+markers", line={"color": "#f59e0b", "width": 3}))
    trend_chart.add_trace(go.Scatter(x=trend["Day"], y=trend["IT energy (kWh)"], name="IT energy", mode="lines+markers", line={"color": "#16a34a", "width": 3}))
    trend_chart.update_layout(height=255, margin=dict(l=10, r=10, t=10, b=10), legend={"orientation": "h", "y": 1.12}, yaxis_title="kWh")
    st.plotly_chart(trend_chart, use_container_width=True)

with monitor_right:
    st.caption("Cooling efficiency diagnostic")
    cooling_chart = px.scatter(cooling, x="Supply air temperature (°C)", y="Estimated PUE", size="Cooling overhead (kWh)",
                               color="Estimated PUE", color_continuous_scale="RdYlGn_r", size_max=30)
    cooling_chart.update_layout(height=255, margin=dict(l=10, r=10, t=10, b=10), coloraxis_colorbar_title="PUE")
    st.plotly_chart(cooling_chart, use_container_width=True)

st.caption("Hourly facility-load profile")
heatmap_chart = px.imshow(heatmap, labels={"x": "Hour of day", "y": "Day", "color": "Estimated kWh"},
                          x=[f"{hour:02d}:00" for hour in heatmap.columns], y=heatmap.index,
                          color_continuous_scale="YlGnBu", aspect="auto")
heatmap_chart.update_layout(height=310, margin=dict(l=10, r=10, t=10, b=10), coloraxis_colorbar_title="kWh")
st.plotly_chart(heatmap_chart, use_container_width=True)

st.divider()
st.subheader("Improvement planner")
planner_left, planner_right = st.columns([1, 1.25])
with planner_left:
    target_pue = st.slider("Target PUE", min_value=1.05, max_value=2.50, value=float(min(max(round(metrics["pue"], 2), 1.05), 2.50)), step=0.05)
    st.caption("Lower PUE means less facility energy is needed for the same IT workload.")

target_facility_kwh = metrics["it"] * target_pue
energy_saved = max(metrics["facility"] - target_facility_kwh, 0)
cost_saved = energy_saved * electricity_rate
carbon_saved = energy_saved * carbon_factor
with planner_right:
    savings_a, savings_b, savings_c = st.columns(3)
    savings_a.metric("Potential energy reduction", f"{energy_saved:,.0f} kWh")
    savings_b.metric("Potential cost reduction", f"{cost_saved:,.0f}")
    savings_c.metric("Potential carbon reduction", f"{carbon_saved:,.0f} kg CO₂e")
    if target_pue >= metrics["pue"]:
        st.warning("Choose a target PUE below the current PUE to see potential savings.")
    else:
        st.success(f"At a PUE of {target_pue:.2f}, facility energy would fall to {target_facility_kwh:,.0f} kWh for this IT load.")

report = pd.DataFrame([{
    "Period": timeframe, "Facility energy (kWh)": metrics["facility"], "IT energy (kWh)": metrics["it"],
    "Non-IT overhead (kWh)": metrics["non_it"], "PUE": metrics["pue"], "DCiE (%)": metrics["dcie"],
    "Target PUE": target_pue, "Potential energy reduction (kWh)": energy_saved,
    "Potential cost reduction": cost_saved, "Potential carbon reduction (kg CO2e)": carbon_saved,
}])
st.download_button("Download current analysis as CSV", report.to_csv(index=False).encode("utf-8"), "green_it_analysis.csv", "text/csv")
st.caption("Formula: PUE = Total Facility Energy ÷ IT Equipment Energy. DCiE = (IT Equipment Energy ÷ Total Facility Energy) × 100.")
