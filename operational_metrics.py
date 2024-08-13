import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np


def generate_historical_data(config, num_days=90):
    base_data = {
        "avg_handling_time": config["operational_metrics"]["avg_handling_time"],
        "first_call_resolution": config["operational_metrics"]["first_call_resolution"],
        "customer_satisfaction": config["operational_metrics"]["customer_satisfaction"]
    }

    dates = [datetime.now() - timedelta(days=i) for i in range(num_days)]
    data = []

    for date in dates:
        day_data = {
            "Date": date,
            "Avg Handling Time": base_data["avg_handling_time"] + np.random.normal(0, 0.5),
            "First Call Resolution": min(max(base_data["first_call_resolution"] + np.random.normal(0, 0.02), 0), 1),
            "Customer Satisfaction": min(max(base_data["customer_satisfaction"] + np.random.normal(0, 0.1), 1), 5)
        }
        data.append(day_data)

    return pd.DataFrame(data)


def render_operational_metrics(config, num_agents, calls_per_day, mean_call_duration):
    st.header("Operational Metrics")

    # Key Performance Indicators
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Handling Time", f"{config['operational_metrics']['avg_handling_time']} min")
    col2.metric("First Call Resolution Rate", f"{config['operational_metrics']['first_call_resolution']:.2%}")
    col3.metric("Customer Satisfaction", f"{config['operational_metrics']['customer_satisfaction']:.2f}/5")

    # Historical Trends
    historical_data = generate_historical_data(config)

    fig_trends = go.Figure()
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['Avg Handling Time'], name="Avg Handling Time"))
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['First Call Resolution'], name="First Call Resolution"))
    fig_trends.add_trace(
        go.Scatter(x=historical_data['Date'], y=historical_data['Customer Satisfaction'], name="Customer Satisfaction"))
    fig_trends.update_layout(title="Historical Trends of Key Metrics", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig_trends)

    # Call Volume Distribution
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    call_volume = np.random.randint(50, 200, size=(7, 24))
    fig_heatmap = px.imshow(call_volume,
                            labels=dict(x="Hour of Day", y="Day of Week", color="Call Volume"),
                            x=hours,
                            y=days,
                            title="Call Volume Distribution by Hour and Day")
    st.plotly_chart(fig_heatmap)

    # Operational Efficiency Metrics
    total_daily_calls = num_agents * calls_per_day
    total_daily_minutes = total_daily_calls * mean_call_duration
    total_available_minutes = num_agents * 8 * 60  # Assuming 8-hour workday
    utilization_rate = (total_daily_minutes / total_available_minutes) * 100

    efficiency_metrics = pd.DataFrame({
        "Metric": ["Calls per Agent per Day", "Total Daily Call Volume", "Utilization Rate"],
        "Value": [
            f"{calls_per_day:,.0f}",
            f"{total_daily_calls:,.0f}",
            f"{utilization_rate:.2f}%"
        ]
    })
    st.table(efficiency_metrics)

    # Agent Performance Distribution
    agent_performance = np.random.normal(loc=config['operational_metrics']['avg_handling_time'], scale=1,
                                         size=num_agents)
    fig_agent_performance = px.histogram(agent_performance, nbins=20,
                                         labels={'value': 'Average Handling Time (minutes)',
                                                 'count': 'Number of Agents'},
                                         title="Distribution of Agent Performance (Average Handling Time)")
    st.plotly_chart(fig_agent_performance)

    # Key Insights
    st.subheader("Key Insights")
    st.write(
        f"1. The average handling time is {config['operational_metrics']['avg_handling_time']} minutes, with a utilization rate of {utilization_rate:.2f}%.")
    st.write(
        f"2. The first call resolution rate is {config['operational_metrics']['first_call_resolution']:.2%}, indicating room for improvement in resolving customer issues on the first contact.")
    st.write(
        f"3. Customer satisfaction is currently at {config['operational_metrics']['customer_satisfaction']:.2f} out of 5, suggesting potential areas for enhancing the customer experience.")
    st.write(
        "4. The call volume heatmap shows peak hours and days, which can be used for optimizing agent scheduling and resource allocation.")