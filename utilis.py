# -*- coding: utf-8 -*-
# @Author: Qiurui Chen
# @Date: 18/07/2023
# @Last Modified by: Qiurui Chen Contact: rachelchen0831@gmail.com

import matplotlib
matplotlib.rcParams['figure.autolayout'] = True

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.base import _get_chat_history
from dotenv import load_dotenv

import logging
import os

debug = False
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create a file handler to save logs to a file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
# Create a formatter for the logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger.addHandler(file_handler)
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

def log(msg, allowLogging):
    if not allowLogging: return
    logger.info(msg)
    if debug:
        print(msg)


def process_file(headers_info, query, allowLogging):
    prompt = get_sql_prompt(headers_info)
    chat = ChatOpenAI()
    sql_code = chat([SystemMessage(content=prompt), HumanMessage(content=query)]).content
    log(f"SQL code: {sql_code}", allowLogging)
    return sql_code


def get_standalone_query(messages, allowLogging):
    if len(messages) > 2:
        # chat_tuples = [(messages[i]['text'], messages[i + 1]['text']) for i in range(0, len(messages) - 1, 2)]
        chat_tuples = [(messages[i]['content'], messages[i + 1]['content']) for i in range(0, len(messages) - 1, 2)]
        llm = ChatOpenAI()
        question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
        query = question_generator.predict(question=messages[-1]['content'], chat_history=_get_chat_history(chat_tuples))
        log("Standalone Query: " + query, allowLogging)
    else:
        query = messages[-1]['content']
    return query

def formating_query(messages, allowLogging):

    prompt = f'''You are a skilled prompt engineer. 
    You will be provided with a chat history, which is a python dict list. 
    In the list, where each dict represents assistant or user message. 
    '''
    humanPrompt = f'''
    You task is to modify the last user message considering the chat history to make it clear and straightforward for openAI chatbot to conduct the command.
    If there is any error message, please consider the error message. 
    Below is the chat history:''' # '{"role": "assistant", "content": answer}' shows the system message, while '{"role": "user", "content": command}' shows the user command, your task is to re-formate the last user command based on the chat history to make it clear so that chatbot can conduct this command.
    for message_content in messages:
        humanPrompt += f" {message_content} \n"
    humanPrompt += "Please modify the last user command and only return the modified command on behalf of the user."

    chat = ChatOpenAI()
    messages = [
        SystemMessage(content=prompt
        ),
        HumanMessage(
            content=humanPrompt
        ),
    ]
    query = chat(messages).content

    return query

def handle_query_light(columnData, messages, allowLogging):
    # headers_info = json.loads(columnData)
    headers_info =columnData
    message_list = messages
    # message_list = json.loads(messages)
    # query = get_standalone_query(message_list, allowLogging) #predict the query based on the chat history
    query = formating_query(message_list, allowLogging) #predict the query based on the chat history
    # query = messages[-1]['content']
    print("query",query)
    result = process_file(headers_info, query, allowLogging)
    return result



example_queries = {'Make a scatterplot of the men\'s weight in April vs September. Draw a line indicating no weight change.': {
    'file_hash': 'ab4910e850d408819819810c7c8f24825cafe91647e72ab7c56ee971ab0e6360',
    'answer': 'Here\'s a scatterplot of men\'s weight in April vs September. The red dashed line indicates no weight change.',
    'images': ['https://iili.io/Hgbaqhu.png']
},
'Create a scatterplot showing how square footage varies by year, coloring points by their price.': {
    'file_hash': '1b9d664153f785f957df436ec75cefa099ba504174296b00f93709774aa05198',
    'answer': 'Here is a scatterplot of square footage vs. year, with points colored by their price.',
    'images': ['https://iili.io/HgbW2YG.png']
},
'Make a bar graph of the average shortstop height of each team, in descending order.': {
    'file_hash': 'e6159bed9eddf09f4dff55f38dd7b085cfcfee009bb998e693ff9ad653b5a71d',
    'answer': 'Here\'s a bar graph of the average shortstop height of each team, in descending order.',
    'images': ['https://iili.io/HgbMotS.png']
}}


def get_sql_prompt(headers_info):

    ## streamlit:
    prompt = f'''You are a skilled data analyst. Your task is to write Python code that uses plotly to generate graphs and integrate these plots in a Streamlit web app. The graphical visualizations are to be in response to data in a variable called 'csvData', which is a pandas dataframe. The data comprises {len(headers_info)} columns.
        The columns, together with their descriptions, are:
        '''
    for col_name, col_info in headers_info.items():
        prompt += f"- {col_name}: {col_info}\n"
    prompt += f'''\nWrite Python code specifically for generating Plotly graphs. Don't import unrelated libraries. Only return the code that qutote with three apostrophes and python word in the first line.
        Here are hypothetical questions for reference. These examples feature made-up columns, but the actual data will contain columns as described above.
        '''
    prompt += '''Question: Construct a bar graph illustrating the population distribution among different states.
        Python code: 
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        
        # Assuming that 'csvData' is a pandas DataFrame
        def plot_data(csvData):
            fig = px.bar(csvData, x='state', y='population')
            st.plotly_chart(fig)
        
        # Call the function
        plot_data(csvData)

        Question: Generate a scatterplot illustrating the correlation between school tuition and the number of students.
        Python code:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        
        # Assuming that 'csvData' is a pandas DataFrame
        def plot_data(csvData):
            fig = px.scatter(csvData, x='tuition', y='students')
            st.plotly_chart(fig)
        
        # Call the function
        plot_data(csvData)    
        '''

    return prompt




