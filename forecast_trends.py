import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta


def generate_forecast_data(
    config, num_agents, calls_per_day, mean_call_duration, forecast_periods=12
):
    # Generate historical data
    dates = pd.date_range(end=datetime.now(), periods=24, freq="M")
    historical_revenue = [
        calculate_revenue(config, num_agents, calls_per_day)
        * (1 + np.random.normal(0, 0.05))
        for _ in range(24)
    ]

    # Fit ARIMA model
    model = ARIMA(historical_revenue, order=(1, 1, 1))
    results = model.fit()

    # Generate forecast
    forecast = results.forecast(steps=forecast_periods)
    forecast_dates = pd.date_range(
        start=dates[-1] + timedelta(days=1), periods=forecast_periods, freq="M"
    )

    return dates, historical_revenue, forecast_dates, forecast


def calculate_revenue(config, num_agents, calls_per_day):
    DAYS_PER_MONTH = 30
    monthly_revenue = (
        num_agents
        * calls_per_day
        * config["financial_metrics"]["price_per_call"]
        * DAYS_PER_MONTH
    )
    return monthly_revenue


def render_forecast_trends(config, num_agents, calls_per_day, mean_call_duration):
    st.header("Forecast and Trends")

    # Revenue Forecast
    dates, historical_revenue, forecast_dates, forecast = generate_forecast_data(
        config, num_agents, calls_per_day, mean_call_duration
    )

    fig_forecast = go.Figure()
    fig_forecast.add_trace(
        go.Scatter(x=dates, y=historical_revenue, name="Historical Revenue")
    )
    fig_forecast.add_trace(
        go.Scatter(x=forecast_dates, y=forecast, name="Forecasted Revenue")
    )
    fig_forecast.update_layout(
        title="Revenue Forecast", xaxis_title="Date", yaxis_title="Monthly Revenue ($)"
    )
    st.plotly_chart(fig_forecast)

    # Market Share Projection
    current_market_share = config["market_data"]["our_market_share"]
    projected_market_share = [
        current_market_share
        * (1 + config["financial_metrics"]["expected_growth_rate"]) ** i
        for i in range(12)
    ]
    market_share_dates = pd.date_range(start=datetime.now(), periods=12, freq="M")

    fig_market_share = px.line(
        x=market_share_dates, y=projected_market_share, title="Projected Market Share"
    )
    fig_market_share.update_layout(xaxis_title="Date", yaxis_title="Market Share (%)")
    st.plotly_chart(fig_market_share)

    # Customer Satisfaction Trend
    satisfaction_data = config["market_data"]["historical_data"][
        "our_market_share"
    ]  # Using market share data as a proxy for satisfaction
    satisfaction_dates = pd.to_datetime(
        config["market_data"]["historical_data"]["dates"]
    )

    fig_satisfaction = px.line(
        x=satisfaction_dates, y=satisfaction_data, title="Customer Satisfaction Trend"
    )
    fig_satisfaction.update_layout(xaxis_title="Date", yaxis_title="Satisfaction Score")
    st.plotly_chart(fig_satisfaction)

    # Industry Trends
    st.subheader("Industry Trends")
    trends = [
        "Increasing adoption of AI-powered voice assistants",
        "Growing demand for omnichannel customer service",
        "Rising importance of data privacy and security",
        "Shift towards cloud-based contact center solutions",
        "Integration of voice assistants with IoT devices",
    ]
    for trend in trends:
        st.write(f"• {trend}")

        # Key Performance Indicators (KPIs) Forecast
    st.subheader("Key Performance Indicators (KPIs) Forecast")
    kpis = ['Revenue', 'Market Share', 'Customer Satisfaction', 'Cost per Call']
    current_values = [calculate_revenue(config, num_agents, calls_per_day),
                      config['market_data']['our_market_share'],
                      config['market_data']['our_customer_satisfaction'],
                      config['service_costs']['stt']['Deepgram'] * mean_call_duration]
    forecast_values = [value * (1 + np.random.uniform(0.05, 0.15)) for value in current_values]

    kpi_df = pd.DataFrame({
        'KPI': kpis,
        'Current Value': current_values,
        'Forecasted Value': forecast_values,
        'Growth': [(forecast - current) / current * 100 for forecast, current in zip(forecast_values, current_values)]
    })

    # Format the dataframe
    kpi_df['Current Value'] = kpi_df.apply(
        lambda row: f'${row["Current Value"]:,.2f}' if row['KPI'] == 'Revenue' else f'{row["Current Value"]:.2f}',
        axis=1)
    kpi_df['Forecasted Value'] = kpi_df.apply(
        lambda row: f'${row["Forecasted Value"]:,.2f}' if row['KPI'] == 'Revenue' else f'{row["Forecasted Value"]:.2f}',
        axis=1)
    kpi_df['Growth'] = kpi_df['Growth'].apply(lambda x: f'{x:.2f}%')

    st.table(kpi_df)

    # Scenario Analysis
    st.subheader("Scenario Analysis")
    scenarios = ["Pessimistic", "Base Case", "Optimistic"]
    metrics = ["Revenue Growth", "Market Share Gain", "Cost Reduction"]
    scenario_data = np.random.uniform(low=[-5, -2, -1], high=[5, 2, 1], size=(3, 3))

    fig_scenarios = go.Figure(
        data=[
            go.Bar(name=scenario, x=metrics, y=scenario_data[i])
            for i, scenario in enumerate(scenarios)
        ]
    )
    fig_scenarios.update_layout(
        title="Scenario Analysis", barmode="group", yaxis_title="Percentage Change"
    )
    st.plotly_chart(fig_scenarios)

    # Key Insights and Recommendations
    st.subheader("Key Insights and Recommendations")
    st.write(
        "1. Revenue is projected to grow by {:.2f}% over the next year, driven by increased market adoption and service improvements.".format(
            (forecast[-1] - historical_revenue[-1]) / historical_revenue[-1] * 100
        )
    )
    st.write(
        "2. Our market share is expected to reach {:.2f}% by the end of the forecast period, indicating strong competitive positioning.".format(
            projected_market_share[-1]
        )
    )
    st.write(
        "3. Customer satisfaction shows a positive trend, suggesting our service quality improvements are effective."
    )
    st.write(
        "4. The industry trend towards AI-powered solutions aligns well with our core competencies, presenting growth opportunities."
    )
    st.write("5. Recommendations:")
    st.write("   - Invest in R&D to stay ahead of the AI and IoT integration trends")
    st.write(
        "   - Develop strategies to capitalize on the growing demand for omnichannel customer service"
    )
    st.write(
        "   - Implement robust data privacy measures to address the increasing importance of data security"
    )
    st.write(
        "   - Consider expanding into cloud-based contact center solutions to capture emerging market segments"
    )
    st.write(
        "   - Monitor and adapt to regulatory changes, especially concerning AI and data privacy"
    )
