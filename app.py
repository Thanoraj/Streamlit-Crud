import streamlit as st
import openai
import os
import json

openai.api_key = os.getenv("API_KEY")

st.subheader("OpenAI Demo")

txt = st.text_input("Enter your Topic")
num = st.slider("Enter no of Questions", 0, 10, 1)
form = """
    { 
    "Question": "question here", 
    "A": "option A", 
    "B": "option B", 
    "C": "option C", 
    "D": "option D", 
    "Answer": "correct answera"    },
"""

button = st.button("Submit")
if button:
    prompt = "Generate " + \
        str(num) + " of MCQ Questions with Answers in the following topic ;" + \
        str(txt)+" show pnly the output in the response as a json list in the following format " + str(form)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.56,
        max_tokens=2066,
        top_p=1,
        frequency_penalty=0.35,
        presence_penalty=0
    )
    st.write(response)
    output = response.choices[0].text
    # st.write("Output:", output)
    try:
        mcq_list = json.loads(output)
        # Initialization
        if 'mcq_list' not in st.session_state:
            st.session_state['mcq_list'] = mcq_list
        st.write(mcq_list)
    except json.decoder.JSONDecodeError as e:
        st.write("Error: Could not decode JSON data.")
        st.write("JSONDecodeError:", e.msg)
