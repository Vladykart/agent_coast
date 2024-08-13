import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_market_position(config):
    st.header("Market Position")

    # Market Share Comparison
    market_data = pd.DataFrame(
        [
            {
                "Company": "Our Service",
                "Market Share": config["market_data"]["our_market_share"],
                "Customer Satisfaction": config["market_data"][
                    "our_customer_satisfaction"
                ],
                "Price per Call": config["financial_metrics"]["price_per_call"],
            }
        ]
        + [
            {
                "Company": comp["name"],
                "Market Share": comp["market_share"],
                "Customer Satisfaction": comp["customer_satisfaction"],
                "Price per Call": comp["price_per_call"],
            }
            for comp in config["market_data"]["competitors"]
        ]
    )

    fig_market_share = px.pie(
        market_data,
        values="Market Share",
        names="Company",
        title="Market Share Comparison",
    )
    st.plotly_chart(fig_market_share)

    # Price vs Satisfaction Comparison
    fig_satisfaction_price = px.scatter(
        market_data,
        x="Price per Call",
        y="Customer Satisfaction",
        size="Market Share",
        color="Company",
        title="Price vs Satisfaction Comparison",
        labels={
            "Price per Call": "Price per Call ($)",
            "Customer Satisfaction": "Customer Satisfaction Score",
        },
    )
    fig_satisfaction_price.update_layout(xaxis_range=[0.5, 1.5], yaxis_range=[3.5, 5])
    st.plotly_chart(fig_satisfaction_price)

    # Historical Market Share Trend
    historical_data = pd.DataFrame(
        {
            "Date": config["market_data"]["historical_data"]["dates"],
            "Our Market Share": config["market_data"]["historical_data"][
                "our_market_share"
            ],
            "Industry Growth": config["market_data"]["historical_data"][
                "industry_growth"
            ],
        }
    )

    fig_historical = go.Figure()
    fig_historical.add_trace(
        go.Scatter(
            x=historical_data["Date"],
            y=historical_data["Our Market Share"],
            mode="lines+markers",
            name="Our Market Share",
        )
    )
    fig_historical.add_trace(
        go.Scatter(
            x=historical_data["Date"],
            y=historical_data["Industry Growth"],
            mode="lines+markers",
            name="Industry Growth",
        )
    )
    fig_historical.update_layout(
        title="Historical Market Share and Industry Growth",
        xaxis_title="Date",
        yaxis_title="Percentage (%)",
    )
    st.plotly_chart(fig_historical)

    # Competitive Analysis
    st.subheader("Competitive Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Our Market Position",
            f"{len([comp for comp in config['market_data']['competitors'] if config['market_data']['our_market_share'] > comp['market_share']]) + 1} out of {len(config['market_data']['competitors']) + 1}",
        )
        st.metric(
            "Market Share Gap to Leader",
            f"{max(comp['market_share'] for comp in config['market_data']['competitors']) - config['market_data']['our_market_share']:.1f}%",
        )

    with col2:
        st.metric(
            "Price Competitiveness",
            f"{(config['financial_metrics']['price_per_call'] / (sum(comp['price_per_call'] for comp in config['market_data']['competitors'])) / (len(config['market_data']['competitors']) + 1)):.2f}x",
        )
        st.metric(
            "Customer Satisfaction Ranking",
            f"{len([comp for comp in config['market_data']['competitors'] if config['market_data']['our_customer_satisfaction'] > comp['customer_satisfaction']]) + 1} out of {len(config['market_data']['competitors']) + 1}",
        )

    # SWOT Analysis
    st.subheader("SWOT Analysis")
    swot_data = {
        "Strengths": [
            "Advanced AI technology",
            "High customer satisfaction",
            "Competitive pricing",
        ],
        "Weaknesses": [
            "Limited market share",
            "Dependency on third-party services",
            "New entrant in the market",
        ],
        "Opportunities": [
            "Growing demand for AI-powered solutions",
            "Potential for international expansion",
            "Integration with other business systems",
        ],
        "Threats": [
            "Intense competition",
            "Rapid technological changes",
            "Regulatory challenges in AI and data privacy",
        ],
    }

    col1, col2 = st.columns(2)
    for i, (category, items) in enumerate(swot_data.items()):
        with col1 if i % 2 == 0 else col2:
            st.write(f"**{category}**")
            for item in items:
                st.write(f"- {item}")

        # Key Insights
        st.subheader("Key Insights")
        st.write(
            f"1. Our current market share is {config['market_data']['our_market_share']}%, positioning us {len([comp for comp in config['market_data']['competitors'] if config['market_data']['our_market_share'] > comp['market_share']]) + 1} out of {len(config['market_data']['competitors']) + 1} in the market."
        )
        st.write(
            f"2. We have a {max(comp['market_share'] for comp in config['market_data']['competitors']) - config['market_data']['our_market_share']:.1f}% market share gap to close with the market leader."
        )
        st.write(
            f"3. Our customer satisfaction score of {config['market_data']['our_customer_satisfaction']} ranks us {len([comp for comp in config['market_data']['competitors'] if config['market_data']['our_customer_satisfaction'] > comp['customer_satisfaction']]) + 1} out of {len(config['market_data']['competitors']) + 1}, indicating strong performance in customer experience."
        )
        st.write(
            f"4. Our pricing strategy is {'competitive' if config['financial_metrics']['price_per_call'] <= sum(comp['price_per_call'] for comp in config['market_data']['competitors']) / len(config['market_data']['competitors']) else 'premium'}, which aligns with our market positioning."
        )
        st.write(
            "5. The SWOT analysis highlights our technological advantages and the potential for growth, while also identifying areas for improvement and external challenges to monitor."
        )

        # Market Trends and Predictions
        st.subheader("Market Trends and Predictions")

        # Calculate the average growth rate
        growth_rates = [
            (
                config["market_data"]["historical_data"]["our_market_share"][i + 1]
                / config["market_data"]["historical_data"]["our_market_share"][i]
            )
            - 1
            for i in range(
                len(config["market_data"]["historical_data"]["our_market_share"]) - 1
            )
        ]
        avg_growth_rate = sum(growth_rates) / len(growth_rates)

        st.write(
            f"1. Based on historical data, our average market share growth rate is {avg_growth_rate:.2%} per month."
        )
        st.write(
            f"2. The industry is growing at an average rate of {(config['market_data']['historical_data']['industry_growth'][-1] - config['market_data']['historical_data']['industry_growth'][0]) / len(config['market_data']['historical_data']['industry_growth']):.2%} per month."
        )
        st.write(
            "3. Key factors influencing market trends include technological advancements, changing customer preferences, and regulatory developments in AI and data privacy."
        )
        st.write(
            "4. To maintain and improve our market position, we should focus on leveraging our strengths in AI technology and customer satisfaction while addressing our weaknesses and potential threats."
        )
