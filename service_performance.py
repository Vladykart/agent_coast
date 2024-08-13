import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def render_service_performance(config, total_cost_per_minute):
    st.header("Service Performance")

    # Service Comparison Table
    service_data = [
        {
            "Service": "Text Generation",
            "Cost per Minute ($)": (config["service_costs"]["text_generation"]["input"]["cost_per_1k_tokens"] *
                                    config["service_costs"]["text_generation"]["input"]["tokens_per_minute"] / 1000 +
                                    config["service_costs"]["text_generation"]["output"]["cost_per_1k_tokens"] *
                                    config["service_costs"]["text_generation"]["output"]["tokens_per_minute"] / 1000),
            "Accuracy (%)": np.random.uniform(95, 99.9),
            "Latency (ms)": np.random.randint(50, 200)
        },
        {
            "Service": "Audio Recognition",
            "Cost per Minute ($)": config["service_costs"]["audio_recognition"]["deepgram_nova2"]["cost_per_minute"],
            "Accuracy (%)": np.random.uniform(95, 99.9),
            "Latency (ms)": np.random.randint(50, 200)
        },
        {
            "Service": "Audio Generation",
            "Cost per Minute ($)": (config["service_costs"]["audio_generation"]["11labs_scale"]["cost_per_1k_chars"] *
                                    config["service_costs"]["audio_generation"]["11labs_scale"][
                                        "chars_per_minute"] / 1000),
            "Accuracy (%)": np.random.uniform(95, 99.9),
            "Latency (ms)": np.random.randint(50, 200)
        }
    ]

    df_services = pd.DataFrame(service_data)
    df_services["Percentage of Total Cost"] = df_services["Cost per Minute ($)"] / total_cost_per_minute * 100
    df_services["Cost per Minute ($)"] = df_services["Cost per Minute ($)"].apply(lambda x: f"${x:.4f}")
    df_services["Percentage of Total Cost"] = df_services["Percentage of Total Cost"].apply(lambda x: f"{x:.2f}%")
    df_services["Accuracy (%)"] = df_services["Accuracy (%)"].apply(lambda x: f"{x:.2f}%")
    st.table(df_services)

    # Convert the `Percentage of Total Cost` column back to numeric format for plotting
    df_services['Percentage of Total Cost Numeric'] = df_services["Percentage of Total Cost"].str.rstrip('%').astype(float)

    # Radar Chart for Service Quality Comparison
    categories = ['Cost', 'Accuracy', 'Speed']
    fig_radar = go.Figure()

    for index, row in df_services.iterrows():
        cost_value = float(row['Cost per Minute ($)'].replace('$', ''))
        if cost_value == 0:
            cost_value = 1e-6  # Avoid division by zero by setting a very small value

        fig_radar.add_trace(go.Scatterpolar(
            r=[1 / cost_value,
               float(row['Accuracy (%)'].replace('%', '')),
               1 / row['Latency (ms)']],
            theta=categories,
            fill='toself',
            name=row['Service']
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Service Quality Comparison"
    )
    st.plotly_chart(fig_radar)

    # Service Cost Breakdown
    fig_treemap = px.treemap(
        df_services,
        path=['Service'],
        values='Percentage of Total Cost Numeric',
        title="Service Cost Breakdown"
    )
    st.plotly_chart(fig_treemap)

    # Performance Metrics Over Time (Simulated Data)
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    performance_data = []

    for service in df_services['Service']:
        base_accuracy = float(df_services[df_services['Service'] == service]['Accuracy (%)'].values[0].replace('%', ''))
        base_latency = df_services[df_services['Service'] == service]['Latency (ms)'].values[0]

        for date in dates:
            performance_data.append({
                "Date": date,
                "Service": service,
                "Accuracy": min(base_accuracy + np.random.normal(0, 0.5), 100),
                "Latency": max(base_latency + np.random.normal(0, 10), 0)
            })

    df_performance = pd.DataFrame(performance_data)

    fig_performance = go.Figure()
    for service in df_services['Service']:
        service_data = df_performance[df_performance['Service'] == service]
        fig_performance.add_trace(
            go.Scatter(x=service_data['Date'], y=service_data['Accuracy'], name=f"{service} Accuracy"))
        fig_performance.add_trace(
            go.Scatter(x=service_data['Date'], y=service_data['Latency'], name=f"{service} Latency", yaxis="y2"))

    fig_performance.update_layout(
        title="Service Performance Metrics Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Accuracy (%)", range=[90, 100]),
        yaxis2=dict(title="Latency (ms)", overlaying="y", side="right", range=[0, 250]),
        legend=dict(x=1.1, y=1, bordercolor="Black", borderwidth=1)
    )
    st.plotly_chart(fig_performance)

    # Key Insights
    st.subheader("Key Insights")
    most_expensive_service = df_services.iloc[
        df_services['Percentage of Total Cost Numeric'].idxmax()]
    best_accuracy_service = df_services.iloc[
        df_services['Accuracy (%)'].astype(str).str.rstrip('%').astype(float).idxmax()]
    lowest_latency_service = df_services.iloc[df_services['Latency (ms)'].idxmin()]

    st.write(
        f"1. {most_expensive_service['Service']} is the most expensive service, accounting for {most_expensive_service['Percentage of Total Cost']} of the total cost.")
    st.write(
        f"2. {best_accuracy_service['Service']} shows the highest accuracy at {best_accuracy_service['Accuracy (%)']}.")
    st.write(
        f"3. {lowest_latency_service['Service']} has the lowest latency at {lowest_latency_service['Latency (ms)']} ms.")
    st.write(
        "4. Performance metrics over time indicate general stability with some fluctuations. Regular monitoring is recommended to ensure consistent service quality.")
    st.write(
        "5. Consider optimizing the most expensive service or exploring alternative providers to reduce costs while maintaining quality.")
