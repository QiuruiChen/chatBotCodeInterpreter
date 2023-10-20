# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 19/07/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

import streamlit as st
from langchain.chains import ConversationChain
import pandas as pd
from utilis import handle_query_light
import components.authenticate as authenticate
import re

st.set_page_config(page_title="SKIM Chat")
st.title('💬 SKIM Chat App')

# Check authentication
authenticate.set_st_state_vars()
# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()
    st.error("Please login to use this app!")
    st.stop()



def extract_code(text):
    pattern = '```python(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return "No code found."

# Store AI generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "I'm SKIMChat, How may I help you?"}]
# Store CSV data
if "csvData" not in st.session_state.keys():
    st.session_state.csvData = None

with st.sidebar:
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")


st.write("This chatbot will generate code/visualizations/tables based on your input. Please upload a CSV file to get started.")
st.write("Example questions: generate a histogram of the 'rlh' column of the data; Plot the correlation of the data.")
# Hugging Face Credentials
# with st.sidebar:
    # st.header('Hugging Face Login')
    # hf_email = st.text_input('Enter E-mail:', type='password')
    # hf_pass = st.text_input('Enter password:', type='password')



# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # display code if there is any code, otherwise disaply the content
        csvData = st.session_state.csvData
        pythoncode = extract_code(message["content"])
        if (pythoncode != "No code found."):
            # Execute the input string as Python code
            # if "plotly.express" or "st.write" in pythoncode:
            #     exec(pythoncode)
            # else:
            #     st.write(exec(pythoncode))
            exec(pythoncode)
        else:
            if "error" in message["content"]:
                print('message["content"]')
                st.error(message["content"])
            else:
                st.write(message["content"])


# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    if uploaded_file is not None:
        print("uploaded_file",uploaded_file)
        csvData = pd.read_csv(uploaded_file)
        st.session_state.csvData = csvData
        # st.write(data)
        # Create dictionary with column info
        columnData = csvData.dtypes.apply(lambda x: x.name).to_dict()
        messages = st.session_state.messages
        allowLogging = True
        # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # response = generate_response(prompt, hf_email, hf_pass)
                response = handle_query_light(columnData, messages, allowLogging)
                print("response",response)
                pythoncode = extract_code(response)
                print("pythoncode",pythoncode)
                if(pythoncode != "No code found."):
                    try:
                        # Execute the input string as Python code
                        if "plotly.express" in pythoncode:
                            exec(pythoncode)
                        else:
                            st.write(exec(pythoncode))
                    except ValueError as e:
                        st.write(f"Please report this error to AI lab!")
                        st.error(e)
                        response = "error:"+str(e)
                else:
                    st.write(response)
                # else:
                    # if "plotly.express" in response:
                    #     # Execute the input string as Python code
                    #     exec(response)
                    # else:
                    #     st.write(exec(response))

        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
    else:
        st.error("you need at least upload a csv file!")
        st.stop()


