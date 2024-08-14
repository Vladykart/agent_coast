import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def calculate_costs(config, num_agents, calls_per_day, mean_call_duration, selected_services):
    print("Selected services:", selected_services)  # Debugging line

    # Validate the structure of selected_services
    if not isinstance(selected_services, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in selected_services.items()):
        raise ValueError(
            "selected_services must be a dictionary with service categories as keys and service keys as values.")

    # Build the cost data
    cost_data = {
        "Service": ["Landline", "Client Landline"]
                   + [str(service_key) for service_key in
                      selected_services.values()]  # Ensure all service keys are strings
                   + ["SIP"],
        "Cost per Minute ($)": [
                                   config["service_costs"]["other"]["Landline"],
                                   config["service_costs"]["other"]["Client Landline"],
                               ]
                               + [config["service_costs"][category][str(service_key)] for category, service_key in
                                  selected_services.items()]
                               + [config["service_costs"]["other"]["SIP"]],
    }

    df_costs = pd.DataFrame(cost_data)
    df_costs["Total Cost per Minute"] = df_costs["Cost per Minute ($)"]
    df_costs["Daily Cost ($)"] = (
            df_costs["Total Cost per Minute"]
            * num_agents
            * calls_per_day
            * mean_call_duration
    )
    df_costs["Monthly Cost ($)"] = df_costs["Daily Cost ($)"] * DAYS_PER_MONTH
    return df_costs


def calculate_revenue(config, num_agents, calls_per_day):
    DAYS_PER_MONTH = 30
    daily_revenue = (
            num_agents * calls_per_day * config["financial_metrics"]["price_per_call"]
    )
    monthly_revenue = daily_revenue * DAYS_PER_MONTH
    return monthly_revenue


def render_scalability_analysis(config, num_agents, calls_per_day, mean_call_duration, total_cost_per_minute):
    st.header("Scalability Analysis")

    scale_factors = [0.5, 1, 2, 5, 10]
    scale_data = []
    for factor in scale_factors:
        scaled_agents = int(num_agents * factor)
        scaled_costs = scaled_agents * calls_per_day * mean_call_duration * total_cost_per_minute * 30  # Monthly cost
        scaled_revenue = calculate_revenue(config, scaled_agents, calls_per_day)
        scaled_profit = scaled_revenue - scaled_costs
        scale_data.append(
            {
                "Scale": f"{scaled_agents} Agents",
                "Monthly Revenue": scaled_revenue,
                "Monthly Cost": scaled_costs,
                "Monthly Profit": scaled_profit,
                "Profit Margin": (
                    (scaled_profit / scaled_revenue) * 100 if scaled_revenue > 0 else 0
                ),
            }
        )

    df_scale = pd.DataFrame(scale_data)
    st.dataframe(df_scale)

    fig_scale = px.bar(
        df_scale,
        x="Scale",
        y=["Monthly Revenue", "Monthly Cost", "Monthly Profit"],
        title="Financial Metrics at Different Scales",
    )
    st.plotly_chart(fig_scale)

    # Cost per call at different scales
    df_scale["Cost per Call"] = df_scale["Monthly Cost"] / (
            df_scale["Scale"].str.split().str[0].astype(int) * calls_per_day * 30
    )
    fig_cost_per_call = px.line(
        df_scale,
        x="Scale",
        y="Cost per Call",
        title="Cost per Call at Different Scales",
    )
    st.plotly_chart(fig_cost_per_call)

    # Efficiency analysis
    df_scale["Efficiency Score"] = df_scale["Monthly Profit"] / df_scale["Monthly Cost"]
    fig_efficiency = px.line(
        df_scale,
        x="Scale",
        y="Efficiency Score",
        title="Operational Efficiency at Different Scales",
    )
    st.plotly_chart(fig_efficiency)

    # Break-even analysis
    fixed_costs = 100000  # Assume some fixed costs
    variable_costs = df_scale["Monthly Cost"] / (df_scale["Scale"].str.split().str[0].astype(int) * calls_per_day * 30)
    price_per_call = config["financial_metrics"]["price_per_call"]
    break_even_calls = fixed_costs / (price_per_call - variable_costs)

    fig_break_even = px.line(
        df_scale,
        x="Scale",
        y=break_even_calls,
        title="Break-even Number of Calls at Different Scales",
    )
    st.plotly_chart(fig_break_even)

    # Key Insights
    st.subheader("Key Insights")
    optimal_scale = df_scale.loc[df_scale["Profit Margin"].idxmax(), "Scale"]
    st.write(f"1. The optimal scale for maximizing profit margin is {optimal_scale}.")
    st.write(
        f"2. As we scale up, the cost per call {'decreases' if df_scale['Cost per Call'].iloc[-1] < df_scale['Cost per Call'].iloc[0] else 'increases'}, indicating {'economies' if df_scale['Cost per Call'].iloc[-1] < df_scale['Cost per Call'].iloc[0] else 'diseconomies'} of scale."
    )
    st.write(
        f"3. The operational efficiency {'improves' if df_scale['Efficiency Score'].iloc[-1] > df_scale['Efficiency Score'].iloc[0] else 'declines'} as we scale up, suggesting {'positive' if df_scale['Efficiency Score'].iloc[-1] > df_scale['Efficiency Score'].iloc[0] else 'negative'} returns to scale."
    )
    st.write(
        f"4. The break-even number of calls {'decreases' if break_even_calls.iloc[-1] < break_even_calls.iloc[0] else 'increases'} with scale, indicating {'improved' if break_even_calls.iloc[-1] < break_even_calls.iloc[0] else 'reduced'} financial resilience at larger scales."
    )
    st.write(
        "5. Consider the trade-offs between profitability, efficiency, and risk when deciding on the optimal scale for operations."
    )