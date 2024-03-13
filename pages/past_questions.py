import streamlit as st
import os
from streamlit_lottie import st_lottie
import json


def read_past_questions_from_file():
    past_questions = []
    if os.path.exists("questions.txt"):
        with open("questions.txt", "r") as file:
            for line in file:
                past_questions.append(line.strip())
    return past_questions


st.title("EchoBase Past Questions")

# Define layout
col1, col2 = st.columns([1, 3])

# Left column for animations
with col1:
    # Load Lottie animation
    with open("Questions.json", "r") as f:
        lottie_json = json.load(f)
    st_lottie(lottie_json)

    # Right column for contents
with col2:
    past_questions = read_past_questions_from_file()
    if not past_questions:
        st.write("")
        st.write("No past questions yet.")
    else:
        for question in past_questions:
            st.write(question)
