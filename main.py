import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import norm

# Import module functions
from financial_overview import render_financial_overview
from operational_metrics import render_operational_metrics
from service_performance import render_service_performance
from market_position import render_market_position
from scalability_analysis import render_scalability_analysis
from risk_assessment import render_risk_assessment
from forecast_trends import render_forecast_trends
from service_configuration import render_service_configuration

# Initialize session state for configurations
if "config" not in st.session_state:
    st.session_state.config = {
        "service_costs": {
            "text_generation": {
                "input": {"cost_per_1k_tokens": 0.005, "tokens_per_minute": 0.5},
                "output": {"cost_per_1k_tokens": 0.015, "tokens_per_minute": 0.5},
            },
            "audio_recognition": {
                "deepgram_nova2": {"cost_per_minute": 0.0036},
            },
            "audio_generation": {
                "11labs_scale": {"cost_per_1k_chars": 0.18, "chars_per_minute": 150},
            },
        },
        "operational_metrics": {
            "avg_handling_time": 5.0,
            "first_call_resolution": 0.85,
            "customer_satisfaction": 4.5,
        },
        "financial_metrics": {"price_per_call": 1.0, "expected_growth_rate": 0.1},
        "market_data": {
            "our_market_share": 15,
            "our_customer_satisfaction": 4.5,
            "competitors": [
                {
                    "name": "Competitor A",
                    "market_share": 30,
                    "customer_satisfaction": 4.2,
                    "price_per_call": 1.2,
                },
                {
                    "name": "Competitor B",
                    "market_share": 25,
                    "customer_satisfaction": 4.0,
                    "price_per_call": 0.9,
                },
                {
                    "name": "Competitor C",
                    "market_share": 30,
                    "customer_satisfaction": 4.3,
                    "price_per_call": 1.1,
                },
            ],
            "historical_data": {
                "dates": [
                    (datetime.now() - timedelta(days=30 * i)).strftime("%Y-%m-%d")
                    for i in range(12, 0, -1)
                ],
                "our_market_share": [
                    12,
                    12.5,
                    13,
                    13.5,
                    14,
                    14.2,
                    14.5,
                    14.7,
                    14.8,
                    14.9,
                    15,
                    15,
                ],
                "industry_growth": [
                    5,
                    5.2,
                    5.4,
                    5.6,
                    5.8,
                    6,
                    6.2,
                    6.4,
                    6.6,
                    6.8,
                    7,
                    7.2,
                ],
            },
        },
    }

# Sidebar for configuration
st.sidebar.title("Dashboard Configuration")

# Configuration sections
config_sections = [
    "Service Costs",
    "Operational Metrics",
    "Financial Metrics",
    "Market Data",
]
selected_section = st.sidebar.selectbox("Select Configuration Section", config_sections)


# Function to update nested dictionary
def update_nested_dict(d, keys, value):
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


# Configuration UI
if selected_section == "Service Costs":
    st.sidebar.subheader("Text Generation Costs")
    update_nested_dict(st.session_state.config, ["service_costs", "text_generation", "input", "cost_per_1k_tokens"],
                       st.sidebar.number_input("Input Cost per 1K Tokens", value=0.005, format="%.4f", step=0.0001))
    update_nested_dict(st.session_state.config, ["service_costs", "text_generation", "output", "cost_per_1k_tokens"],
                       st.sidebar.number_input("Output Cost per 1K Tokens", value=0.015, format="%.4f", step=0.0001))

    st.sidebar.subheader("Audio Recognition Costs")
    update_nested_dict(st.session_state.config,
                       ["service_costs", "audio_recognition", "deepgram_nova2", "cost_per_minute"],
                       st.sidebar.number_input("Deepgram Nova-2 Cost per Minute", value=0.0036, format="%.4f",
                                               step=0.0001))

    st.sidebar.subheader("Audio Generation Costs")
    update_nested_dict(st.session_state.config,
                       ["service_costs", "audio_generation", "11labs_scale", "cost_per_1k_chars"],
                       st.sidebar.number_input("11labs Scale Cost per 1K Characters", value=0.18, format="%.4f",
                                               step=0.01))

elif selected_section == "Operational Metrics":
    update_nested_dict(st.session_state.config, ["operational_metrics", "avg_handling_time"],
                       st.sidebar.number_input("Average Handling Time (minutes)", value=5.0, step=0.1))
    update_nested_dict(st.session_state.config, ["operational_metrics", "first_call_resolution"],
                       st.sidebar.number_input("First Call Resolution Rate", value=0.85, min_value=0.0, max_value=1.0,
                                               step=0.01))
    update_nested_dict(st.session_state.config, ["operational_metrics", "customer_satisfaction"],
                       st.sidebar.number_input("Customer Satisfaction Score", value=4.5, min_value=1.0, max_value=5.0,
                                               step=0.1))

elif selected_section == "Financial Metrics":
    update_nested_dict(st.session_state.config, ["financial_metrics", "price_per_call"],
                       st.sidebar.number_input("Price per Call ($)", value=1.0, step=0.01))
    update_nested_dict(st.session_state.config, ["financial_metrics", "expected_growth_rate"],
                       st.sidebar.number_input("Expected Growth Rate", value=0.1, format="%.2f", step=0.01))

elif selected_section == "Market Data":
    update_nested_dict(st.session_state.config, ["market_data", "our_market_share"],
                       st.sidebar.number_input("Our Market Share (%)", value=15.0, step=0.1))
    update_nested_dict(st.session_state.config, ["market_data", "our_customer_satisfaction"],
                       st.sidebar.number_input("Our Customer Satisfaction", value=4.5, min_value=1.0, max_value=5.0,
                                               step=0.1))

# Main dashboard inputs
st.sidebar.title("Simulation Parameters")
num_agents = st.sidebar.slider(
    "Number of Agents:", min_value=1, max_value=10000, value=100, step=1
)
calls_per_day = st.sidebar.slider(
    "Calls per Day (per agent):", min_value=1, max_value=1000, value=50, step=1
)
mean_call_duration = st.sidebar.slider(
    "Mean Call Duration (minutes):",
    min_value=1.0,
    max_value=60.0,
    value=float(st.session_state.config["operational_metrics"]["avg_handling_time"]),
    step=0.1
)


# Calculate total cost per minute
def calculate_total_cost_per_minute(config):
    text_gen_cost = (config["service_costs"]["text_generation"]["input"]["cost_per_1k_tokens"] *
                     config["service_costs"]["text_generation"]["input"]["tokens_per_minute"] / 1000 +
                     config["service_costs"]["text_generation"]["output"]["cost_per_1k_tokens"] *
                     config["service_costs"]["text_generation"]["output"]["tokens_per_minute"] / 1000)
    audio_recog_cost = config["service_costs"]["audio_recognition"]["deepgram_nova2"]["cost_per_minute"]
    audio_gen_cost = (config["service_costs"]["audio_generation"]["11labs_scale"]["cost_per_1k_chars"] *
                      config["service_costs"]["audio_generation"]["11labs_scale"]["chars_per_minute"] / 1000)
    return text_gen_cost + audio_recog_cost + audio_gen_cost


total_cost_per_minute = calculate_total_cost_per_minute(st.session_state.config)
st.sidebar.metric("Total Cost per Minute", f"${total_cost_per_minute:.4f}")

# Main dashboard
st.title("LiveKit Voice Assistant Business Intelligence Dashboard")

# Tabs for different modules
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Financial Overview",
    "Operational Metrics",
    "Service Performance",
    "Market Position",
    "Scalability Analysis",
    "Risk Assessment",
    "Forecast and Trends",
    "Service Configuration",  # New tab
])

# Render each module in its respective tab
with tab1:
    render_financial_overview(st.session_state.config, num_agents, calls_per_day, mean_call_duration,
                              total_cost_per_minute)

with tab2:
    render_operational_metrics(st.session_state.config, num_agents, calls_per_day, mean_call_duration)

with tab3:
    render_service_performance(st.session_state.config, total_cost_per_minute)

with tab4:
    render_market_position(st.session_state.config)

with tab5:
    render_scalability_analysis(st.session_state.config, num_agents, calls_per_day, mean_call_duration,
                                total_cost_per_minute)

with tab6:
    render_risk_assessment(st.session_state.config, num_agents, calls_per_day, mean_call_duration)

with tab7:
    render_forecast_trends(st.session_state.config, num_agents, calls_per_day, mean_call_duration)

with tab8:
    render_service_configuration(st.session_state.config)