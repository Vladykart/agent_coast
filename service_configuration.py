import streamlit as st
import pandas as pd
import plotly.express as px


def initialize_config_state(config):
    if 'config' not in st.session_state:
        st.session_state.config = config
    if 'llm_option' not in st.session_state:
        st.session_state.llm_option = st.session_state.config['service_costs']['text_generation'].get('model', 'gpt-4o')
    if 'stt_option' not in st.session_state:
        st.session_state.stt_option = st.session_state.config['service_costs']['audio_recognition'].get('provider',
                                                                                                        'deepgram')
    if 'tts_option' not in st.session_state:
        st.session_state.tts_option = st.session_state.config['service_costs']['audio_generation'].get('provider',
                                                                                                       'elevenlabs')


def update_config(key, value):
    st.session_state.config = st.session_state.config.copy()
    keys = key.split('.')
    d = st.session_state.config
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def render_service_configuration(config):
    initialize_config_state(config)

    st.header("Service Configuration and Cost Comparison")

    # Service configuration
    st.subheader("Service Configuration")

    # LLM Selection
    st.write("Language Model (LLM)")
    llm_option = st.radio(
        "Select LLM Service",
        ("gpt-4o", "gpt-4oMini"),
        key="llm_radio"
    )

    if llm_option != st.session_state.llm_option:
        st.session_state.llm_option = llm_option
        update_config('service_costs.text_generation.model', llm_option)

    if llm_option == "gpt-4o":
        input_cost = st.number_input(
            "GPT-4O Input Cost per 1K Tokens ($)",
            value=st.session_state.config['service_costs']['text_generation']['input'].get('cost_per_1k_tokens', 0.005),
            format="%.4f",
            key="gpt4o_input_cost"
        )
        update_config('service_costs.text_generation.input.cost_per_1k_tokens', input_cost)

        output_cost = st.number_input(
            "GPT-4O Output Cost per 1K Tokens ($)",
            value=st.session_state.config['service_costs']['text_generation']['output'].get('cost_per_1k_tokens',
                                                                                            0.015),
            format="%.4f",
            key="gpt4o_output_cost"
        )
        update_config('service_costs.text_generation.output.cost_per_1k_tokens', output_cost)
    else:
        input_cost = st.number_input(
            "GPT-4O Mini Input Cost per 1K Tokens ($)",
            value=st.session_state.config['service_costs']['text_generation']['input'].get('cost_per_1k_tokens', 0.003),
            format="%.4f",
            key="gpt4o_mini_input_cost"
        )
        update_config('service_costs.text_generation.input.cost_per_1k_tokens', input_cost)

        output_cost = st.number_input(
            "GPT-4O Mini Output Cost per 1K Tokens ($)",
            value=st.session_state.config['service_costs']['text_generation']['output'].get('cost_per_1k_tokens',
                                                                                            0.009),
            format="%.4f",
            key="gpt4o_mini_output_cost"
        )
        update_config('service_costs.text_generation.output.cost_per_1k_tokens', output_cost)

    # STT Selection
    st.write("Speech-to-Text (STT)")
    stt_option = st.radio(
        "Select STT Service",
        ("deepgram", "whisper"),
        key="stt_radio"
    )

    if stt_option != st.session_state.stt_option:
        st.session_state.stt_option = stt_option
        update_config('service_costs.audio_recognition.provider', stt_option)

    if stt_option == "deepgram":
        deepgram_cost = st.number_input(
            "Deepgram Nova-2 Cost per Minute ($)",
            value=st.session_state.config['service_costs']['audio_recognition']['deepgram_nova2'].get('cost_per_minute',
                                                                                                      0.0036),
            format="%.4f",
            key="deepgram_cost"
        )
        update_config('service_costs.audio_recognition.deepgram_nova2.cost_per_minute', deepgram_cost)
    else:
        whisper_cost = st.number_input(
            "Whisper Cost per Minute ($)",
            value=st.session_state.config['service_costs']['audio_recognition'].get('whisper', 0.006),
            format="%.4f",
            key="whisper_cost"
        )
        update_config('service_costs.audio_recognition.whisper', whisper_cost)

    # TTS Selection
    st.write("Text-to-Speech (TTS)")
    tts_option = st.radio(
        "Select TTS Service",
        ("elevenlabs", "deepgram_tts"),
        key="tts_radio"
    )

    if tts_option != st.session_state.tts_option:
        st.session_state.tts_option = tts_option
        update_config('service_costs.audio_generation.provider', tts_option)

    if tts_option == "elevenlabs":
        elevenlabs_cost = st.number_input(
            "ElevenLabs Cost per 1K Characters ($)",
            value=st.session_state.config['service_costs']['audio_generation']['11labs_scale'].get('cost_per_1k_chars',
                                                                                                   0.18),
            format="%.4f",
            key="elevenlabs_cost"
        )
        update_config('service_costs.audio_generation.11labs_scale.cost_per_1k_chars', elevenlabs_cost)
    else:
        deepgram_tts_cost = st.number_input(
            "Deepgram TTS Cost per 1K Characters ($)",
            value=st.session_state.config['service_costs']['audio_generation'].get('deepgram_tts', 0.15),
            format="%.4f",
            key="deepgram_tts_cost"
        )
        update_config('service_costs.audio_generation.deepgram_tts', deepgram_tts_cost)

    # Cost Comparison
    st.subheader("Cost Comparison")

    # Calculate costs per minute
    costs = {
        f"LLM ({llm_option})": (
                    st.session_state.config['service_costs']['text_generation']['input']['cost_per_1k_tokens'] *
                    st.session_state.config['service_costs']['text_generation']['input'].get('tokens_per_minute',
                                                                                             0.5) / 1000 +
                    st.session_state.config['service_costs']['text_generation']['output']['cost_per_1k_tokens'] *
                    st.session_state.config['service_costs']['text_generation']['output'].get('tokens_per_minute',
                                                                                              0.5) / 1000),
        f"STT ({stt_option})": st.session_state.config['service_costs']['audio_recognition'][
            stt_option if stt_option != 'deepgram' else 'deepgram_nova2']['cost_per_minute'],
        f"TTS ({tts_option})": (st.session_state.config['service_costs']['audio_generation'][
                                    tts_option if tts_option != 'elevenlabs' else '11labs_scale']['cost_per_1k_chars'] *
                                st.session_state.config['service_costs']['audio_generation'].get('chars_per_minute',
                                                                                                 150) / 1000)
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
    baseline_service = st.selectbox("Select baseline service for comparison", list(costs.keys()),
                                    key="baseline_service")
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

    return st.session_state.config