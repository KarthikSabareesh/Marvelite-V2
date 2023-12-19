import streamlit as st


def trubrics_config(default_component: bool = True):
    st.subheader("Welcome to Marvelite")
    st.subheader("The raw feedback you send will be shown below")
    # email = st.text_input(
    #     label="email", placeholder="email", label_visibility="collapsed"
    # )

    # password = st.text_input(
    #     label="password",
    #     placeholder="password",
    #     label_visibility="collapsed",
    #     type="password"
    # )

    email="karthiksabareesh1503@gmail.com"
    password="KarthikSab-45"

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