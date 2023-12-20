import streamlit as st


def trubrics_config(default_component: bool = True):
    email = st.secrets["EMAIL"]
    password = st.secrets["PASSWORD"]

    if default_component:
        return email, password

    feedback_component = st.text_input(
        label="feedback_component",
        placeholder="Feedback component name",
        label_visibility="collapsed",
    )

    feedback_type = st.radio(
        label="Select the component feedback type:", options=("faces", "thumbs", "textbox"), horizontal=True
    )

    return email, password, feedback_component, feedback_type
