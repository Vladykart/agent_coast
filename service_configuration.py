import streamlit as st
import pandas as pd
import plotly.express as px


def render_service_configuration(config):
    st.header("Service Configuration and Cost Comparison")

    # Service configuration
    st.subheader("Service Configuration")

    # LLM Selection
    st.write("Language Model (LLM)")
    llm_option = st.radio(
        "Select LLM Service",
        ("gpt-4o", "gpt-4oMini"),
        index=0 if config['service_costs']['text_generation'].get('model', 'gpt-4o') == 'gpt-4o' else 1
    )

    if llm_option == "gpt-4o":
        config['service_costs']['text_generation']['model'] = 'gpt-4o'
        config['service_costs']['text_generation']['input']['cost_per_1k_tokens'] = st.number_input(
            "GPT-4O Input Cost per 1K Tokens ($)",
            value=config['service_costs']['text_generation']['input'].get('cost_per_1k_tokens', 0.005),
            format="%.4f"
        )
        config['service_costs']['text_generation']['output']['cost_per_1k_tokens'] = st.number_input(
            "GPT-4O Output Cost per 1K Tokens ($)",
            value=config['service_costs']['text_generation']['output'].get('cost_per_1k_tokens', 0.015),
            format="%.4f"
        )
    else:
        config['service_costs']['text_generation']['model'] = 'gpt-4oMini'
        config['service_costs']['text_generation']['input']['cost_per_1k_tokens'] = st.number_input(
            "GPT-4O Mini Input Cost per 1K Tokens ($)",
            value=config['service_costs']['text_generation']['input'].get('cost_per_1k_tokens', 0.003),
            format="%.4f"
        )
        config['service_costs']['text_generation']['output']['cost_per_1k_tokens'] = st.number_input(
            "GPT-4O Mini Output Cost per 1K Tokens ($)",
            value=config['service_costs']['text_generation']['output'].get('cost_per_1k_tokens', 0.009),
            format="%.4f"
        )

    # STT Selection
    st.write("Speech-to-Text (STT)")
    stt_option = st.radio(
        "Select STT Service",
        ("deepgram", "whisper"),
        index=0 if config['service_costs']['audio_recognition'].get('provider', 'deepgram') == 'deepgram' else 1
    )

    if stt_option == "deepgram":
        config['service_costs']['audio_recognition']['provider'] = 'deepgram'
        config['service_costs']['audio_recognition']['deepgram_nova2']['cost_per_minute'] = st.number_input(
            "Deepgram Nova-2 Cost per Minute ($)",
            value=config['service_costs']['audio_recognition']['deepgram_nova2'].get('cost_per_minute', 0.0036),
            format="%.4f"
        )
    else:
        config['service_costs']['audio_recognition']['provider'] = 'whisper'
        config['service_costs']['audio_recognition']['whisper'] = st.number_input(
            "Whisper Cost per Minute ($)",
            value=config['service_costs']['audio_recognition'].get('whisper', 0.006),
            format="%.4f"
        )

    # TTS Selection
    st.write("Text-to-Speech (TTS)")
    tts_option = st.radio(
        "Select TTS Service",
        ("elevenlabs", "deepgram_tts"),
        index=0 if config['service_costs']['audio_generation'].get('provider', 'elevenlabs') == 'elevenlabs' else 1
    )

    if tts_option == "elevenlabs":
        config['service_costs']['audio_generation']['provider'] = 'elevenlabs'
        config['service_costs']['audio_generation']['11labs_scale']['cost_per_1k_chars'] = st.number_input(
            "ElevenLabs Cost per 1K Characters ($)",
            value=config['service_costs']['audio_generation']['11labs_scale'].get('cost_per_1k_chars', 0.18),
            format="%.4f"
        )
    else:
        config['service_costs']['audio_generation']['provider'] = 'deepgram_tts'
        config['service_costs']['audio_generation']['deepgram_tts'] = st.number_input(
            "Deepgram TTS Cost per 1K Characters ($)",
            value=config['service_costs']['audio_generation'].get('deepgram_tts', 0.15),
            format="%.4f"
        )

    # Cost Comparison
    st.subheader("Cost Comparison")

    # Calculate costs per minute
    costs = {
        f"LLM ({llm_option})": (config['service_costs']['text_generation']['input']['cost_per_1k_tokens'] *
                                config['service_costs']['text_generation']['input'].get('tokens_per_minute',
                                                                                        0.5) / 1000 +
                                config['service_costs']['text_generation']['output']['cost_per_1k_tokens'] *
                                config['service_costs']['text_generation']['output'].get('tokens_per_minute',
                                                                                         0.5) / 1000),
        f"STT ({stt_option})":
            config['service_costs']['audio_recognition'][stt_option if stt_option != 'deepgram' else 'deepgram_nova2'][
                'cost_per_minute'],
        f"TTS ({tts_option})": (config['service_costs']['audio_generation'][
                                    tts_option if tts_option != 'elevenlabs' else '11labs_scale']['cost_per_1k_chars'] *
                                config['service_costs']['audio_generation'].get('chars_per_minute', 150) / 1000)
    }

    # Create DataFrame for comparison
    df_costs = pd.DataFrame(list(costs.items()), columns=['Service', 'Cost per Minute ($)'])

    # Bar chart for cost comparison
    fig = px.bar(df_costs, x='Service', y='Cost per Minute ($)', title='Service Cost Comparison (per Minute)')
    st.plotly_chart(fig)

    # Display cost table
    st.table(df_costs)

    # Calculate and display total cost per minute
    total_cost_per_minute = sum(costs.values())
    st.metric("Total Cost per Minute", f"${total_cost_per_minute:.4f}")

    # Cost breakdown pie chart
    fig_pie = px.pie(df_costs, values='Cost per Minute ($)', names='Service', title='Cost Breakdown')
    st.plotly_chart(fig_pie)

    # Savings comparison
    st.subheader("Potential Savings")
    baseline_service = st.selectbox("Select baseline service for comparison", list(costs.keys()))
    baseline_cost = costs[baseline_service]

    savings = {}
    for service, cost in costs.items():
        if service != baseline_service:
            savings[service] = baseline_cost - cost

    df_savings = pd.DataFrame(list(savings.items()), columns=['Service', 'Savings per Minute ($)'])
    df_savings['Savings per Minute ($)'] = df_savings['Savings per Minute ($)'].apply(lambda x: f"${x:.4f}")
    st.table(df_savings)

    st.write(f"Positive values indicate potential savings compared to {baseline_service}.")
    st.write(f"Negative values indicate {baseline_service} is cheaper.")

    # Update session state
    st.session_state.config = config