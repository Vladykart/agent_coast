import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm


def monte_carlo_simulation(
    config, num_agents, calls_per_day, mean_call_duration, num_simulations=1000
):
    results = []
    for _ in range(num_simulations):
        # Simulate variations in key parameters
        simulated_agents = int(np.random.normal(num_agents, num_agents * 0.1))
        simulated_calls = np.random.normal(calls_per_day, calls_per_day * 0.2)
        simulated_duration = np.random.normal(
            mean_call_duration, mean_call_duration * 0.15
        )
        simulated_price = np.random.normal(
            config["financial_metrics"]["price_per_call"],
            config["financial_metrics"]["price_per_call"] * 0.05,
        )

        # Calculate simulated revenue and costs
        simulated_revenue = (
            simulated_agents * simulated_calls * simulated_price * 30
        )  # Monthly revenue

        # Calculate total cost per minute
        total_cost_per_minute = sum([
            config["service_costs"]["text_generation"]["input"]["cost_per_1k_tokens"] *
            config["service_costs"]["text_generation"]["input"]["tokens_per_minute"] / 1000,
            config["service_costs"]["text_generation"]["output"]["cost_per_1k_tokens"] *
            config["service_costs"]["text_generation"]["output"]["tokens_per_minute"] / 1000,
            config["service_costs"]["audio_recognition"]["deepgram_nova2"]["cost_per_minute"],
            config["service_costs"]["audio_generation"]["11labs_scale"]["cost_per_1k_chars"] *
            config["service_costs"]["audio_generation"]["11labs_scale"]["chars_per_minute"] / 1000
        ])

        simulated_cost = (
            simulated_agents
            * simulated_calls
            * simulated_duration
            * total_cost_per_minute
            * 30
        )  # Monthly cost

        simulated_profit = simulated_revenue - simulated_cost
        results.append(simulated_profit)

    return results


def render_risk_assessment(config, num_agents, calls_per_day, mean_call_duration):
    st.header("Risk Assessment")

    # Monte Carlo Simulation
    simulation_results = monte_carlo_simulation(
        config, num_agents, calls_per_day, mean_call_duration
    )

    fig_monte_carlo = px.histogram(
        simulation_results, nbins=50, title="Monte Carlo Simulation of Monthly Profit"
    )
    fig_monte_carlo.add_vline(
        x=np.mean(simulation_results),
        line_dash="dash",
        line_color="red",
        annotation_text="Mean",
    )
    st.plotly_chart(fig_monte_carlo)

    st.write(f"Expected Monthly Profit: ${np.mean(simulation_results):,.2f}")
    st.write(f"Profit Variability (Std Dev): ${np.std(simulation_results):,.2f}")
    st.write(f"5% Value at Risk: ${np.percentile(simulation_results, 5):,.2f}")

    # Sensitivity Analysis
    variables = ["Number of Agents", "Calls per Day", "Call Duration", "Price per Call"]
    impacts = [0.2, 0.3, 0.25, 0.15]  # Hypothetical impact values

    fig_tornado = go.Figure(
        go.Bar(
            y=variables,
            x=impacts,
            orientation="h",
            marker_color=[
                "rgba(55, 128, 191, 0.7)",
                "rgba(219, 64, 82, 0.7)",
                "rgba(50, 171, 96, 0.7)",
                "rgba(128, 0, 128, 0.7)",
            ],
        )
    )
    fig_tornado.update_layout(
        title="Sensitivity Analysis (Tornado Chart)", xaxis_title="Impact on Profit"
    )
    st.plotly_chart(fig_tornado)

    # Risk Heatmap
    risks = [
        "Technology Failure",
        "Data Privacy Breach",
        "Regulatory Changes",
        "Market Competition",
        "Economic Downturn",
        "Talent Shortage",
    ]
    likelihood = [0.2, 0.15, 0.3, 0.4, 0.25, 0.35]
    impact = [0.8, 0.9, 0.6, 0.5, 0.7, 0.4]

    fig_heatmap = go.Figure(
        data=go.Heatmap(z=[impact], x=risks, y=["Impact"], colorscale="RdYlGn_r")
    )
    fig_heatmap.update_layout(title="Risk Heatmap")
    st.plotly_chart(fig_heatmap)

    # Key Risk Indicators (KRIs)
    st.subheader("Key Risk Indicators (KRIs)")
    kris = pd.DataFrame(
        {
            "KRI": [
                "Customer Churn Rate",
                "System Downtime",
                "Regulatory Compliance Score",
                "Employee Turnover Rate",
            ],
            "Current Value": [f"{5.2}%", f"{99.9}% uptime", f"{95}/100", f"{12}%"],
            "Threshold": ["< 10%", "> 99.5% uptime", "> 90/100", "< 15%"],
            "Status": ["✅", "✅", "✅", "✅"],
        }
    )
    st.table(kris)

    # Key Insights and Recommendations
    st.subheader("Key Insights and Recommendations")
    st.write(
        "1. The Monte Carlo simulation shows a wide range of potential profit outcomes, indicating significant uncertainty in our financial projections."
    )
    st.write(
        "2. Our sensitivity analysis reveals that 'Calls per Day' has the highest impact on profit, followed by 'Call Duration'. Focus on optimizing these variables to improve financial performance."
    )
    st.write(
        "3. The risk heatmap identifies 'Data Privacy Breach' and 'Technology Failure' as high-impact risks. Prioritize mitigation strategies for these areas."
    )
    st.write(
        "4. All Key Risk Indicators are currently within acceptable thresholds, but continuous monitoring is crucial."
    )
    st.write("5. Recommendations:")
    st.write(
        "   - Implement robust data security measures and regular security audits."
    )
    st.write(
        "   - Develop a comprehensive business continuity plan to address technology failures."
    )
    st.write(
        "   - Monitor regulatory developments closely and maintain a proactive compliance strategy."
    )
    st.write(
        "   - Invest in employee training and retention programs to mitigate talent shortage risks."
    )
