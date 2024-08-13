import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def calculate_costs(
    config, num_agents, calls_per_day, mean_call_duration, total_cost_per_minute
):
    DAYS_PER_MONTH = 30
    total_minutes_per_month = (
        num_agents * calls_per_day * mean_call_duration * DAYS_PER_MONTH
    )
    total_cost = total_minutes_per_month * total_cost_per_minute

    cost_breakdown = {
        "Text Generation": (
            config["service_costs"]["text_generation"]["input"]["cost_per_1k_tokens"]
            * config["service_costs"]["text_generation"]["input"]["tokens_per_minute"]
            / 1000
            + config["service_costs"]["text_generation"]["output"]["cost_per_1k_tokens"]
            * config["service_costs"]["text_generation"]["output"]["tokens_per_minute"]
            / 1000
        )
        * total_minutes_per_month,
        "Audio Recognition": config["service_costs"]["audio_recognition"][
            "deepgram_nova2"
        ]["cost_per_minute"]
        * total_minutes_per_month,
        "Audio Generation": (
            config["service_costs"]["audio_generation"]["11labs_scale"][
                "cost_per_1k_chars"
            ]
            * config["service_costs"]["audio_generation"]["11labs_scale"][
                "chars_per_minute"
            ]
            / 1000
        )
        * total_minutes_per_month,
    }

    return pd.DataFrame(
        list(cost_breakdown.items()), columns=["Service", "Monthly Cost ($)"]
    )


def calculate_revenue(config, num_agents, calls_per_day):
    DAYS_PER_MONTH = 30
    monthly_revenue = (
        num_agents
        * calls_per_day
        * config["financial_metrics"]["price_per_call"]
        * DAYS_PER_MONTH
    )
    return monthly_revenue


def render_financial_overview(
    config, num_agents, calls_per_day, mean_call_duration, total_cost_per_minute
):
    st.header("Financial Overview")

    df_costs = calculate_costs(
        config, num_agents, calls_per_day, mean_call_duration, total_cost_per_minute
    )
    total_monthly_cost = df_costs["Monthly Cost ($)"].sum()
    monthly_revenue = calculate_revenue(config, num_agents, calls_per_day)
    monthly_profit = monthly_revenue - total_monthly_cost
    profit_margin = (
        (monthly_profit / monthly_revenue) * 100 if monthly_revenue > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Revenue", f"${monthly_revenue:,.2f}")
    col2.metric("Monthly Cost", f"${total_monthly_cost:,.2f}")
    col3.metric("Monthly Profit", f"${monthly_profit:,.2f}")
    col4.metric("Profit Margin", f"{profit_margin:.2f}%")

    # Revenue vs Cost Breakdown
    fig_revenue_cost = go.Figure()
    fig_revenue_cost.add_trace(
        go.Bar(x=["Revenue"], y=[monthly_revenue], name="Revenue")
    )
    for index, row in df_costs.iterrows():
        fig_revenue_cost.add_trace(
            go.Bar(x=["Costs"], y=[row["Monthly Cost ($)"]], name=row["Service"])
        )
    fig_revenue_cost.update_layout(
        title="Monthly Revenue vs Cost Breakdown", barmode="stack"
    )
    st.plotly_chart(fig_revenue_cost)

    # Profit Trend Projection
    growth_rate = config["financial_metrics"]["expected_growth_rate"]
    dates = [datetime.now() + timedelta(days=x) for x in range(365)]
    profit_trend = pd.DataFrame(
        {
            "Date": dates,
            "Projected Profit": [
                monthly_profit * (1 + (i / 365) * growth_rate) for i in range(365)
            ],
        }
    )
    fig_profit_trend = px.line(
        profit_trend,
        x="Date",
        y="Projected Profit",
        title=f"Projected Annual Profit Trend (Growth Rate: {growth_rate:.1%})",
    )
    st.plotly_chart(fig_profit_trend)

    # Cost Breakdown
    fig_cost_breakdown = px.pie(
        df_costs,
        values="Monthly Cost ($)",
        names="Service",
        title="Monthly Cost Breakdown by Service",
    )
    st.plotly_chart(fig_cost_breakdown)

    # Financial Metrics Table
    financial_metrics = pd.DataFrame(
        {
            "Metric": [
                "Revenue per Call",
                "Cost per Call",
                "Profit per Call",
                "Break-even Calls per Month",
            ],
            "Value": [
                f"${config['financial_metrics']['price_per_call']:.2f}",
                f"${(total_monthly_cost / (num_agents * calls_per_day * 30)):.2f}",
                f"${(monthly_profit / (num_agents * calls_per_day * 30)):.2f}",
                f"{int(total_monthly_cost / config['financial_metrics']['price_per_call']):,}",
            ],
        }
    )
    st.table(financial_metrics)

    # Cost per Minute Breakdown
    st.subheader("Cost per Minute Breakdown")
    cost_per_minute = pd.DataFrame(
        {
            "Service": ["Text Generation", "Audio Recognition", "Audio Generation"],
            "Cost per Minute ($)": [
                config["service_costs"]["text_generation"]["input"][
                    "cost_per_1k_tokens"
                ]
                * config["service_costs"]["text_generation"]["input"][
                    "tokens_per_minute"
                ]
                / 1000
                + config["service_costs"]["text_generation"]["output"][
                    "cost_per_1k_tokens"
                ]
                * config["service_costs"]["text_generation"]["output"][
                    "tokens_per_minute"
                ]
                / 1000,
                config["service_costs"]["audio_recognition"]["deepgram_nova2"][
                    "cost_per_minute"
                ],
                config["service_costs"]["audio_generation"]["11labs_scale"][
                    "cost_per_1k_chars"
                ]
                * config["service_costs"]["audio_generation"]["11labs_scale"][
                    "chars_per_minute"
                ]
                / 1000,
            ],
        }
    )
    cost_per_minute["Percentage"] = (
        cost_per_minute["Cost per Minute ($)"]
        / cost_per_minute["Cost per Minute ($)"].sum()
        * 100
    )
    cost_per_minute["Cost per Minute ($)"] = cost_per_minute[
        "Cost per Minute ($)"
    ].apply(lambda x: f"${x:.4f}")
    cost_per_minute["Percentage"] = cost_per_minute["Percentage"].apply(
        lambda x: f"{x:.2f}%"
    )
    st.table(cost_per_minute)

    # Key Insights
    st.subheader("Key Financial Insights")
    st.write(
        f"1. The current profit margin is {profit_margin:.2f}%, indicating {'a healthy' if profit_margin > 20 else 'an area for improvement in'} profitability."
    )
    st.write(
        f"2. The largest cost component is {df_costs.iloc[df_costs['Monthly Cost ($)'].idxmax()]['Service']}, accounting for {df_costs['Monthly Cost ($)'].max() / total_monthly_cost * 100:.2f}% of total costs."
    )
    st.write(
        f"3. To break even, we need to handle at least {int(total_monthly_cost / config['financial_metrics']['price_per_call']):,} calls per month."
    )
    st.write(
        f"4. The projected annual profit trend shows {'an increasing' if growth_rate > 0 else 'a decreasing'} pattern, with an expected growth rate of {growth_rate:.1%}."
    )
    st.write(
        "5. Consider strategies to reduce costs or increase revenue to improve overall financial performance."
    )
