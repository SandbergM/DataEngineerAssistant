

import matplotlib.pyplot as plt
import anthropic
from anthropic import InternalServerError
import streamlit as st
import seaborn as sns
import pandas as pd
from dotenv import load_dotenv
import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import time 


if os.getenv('ANTHROPIC_API_KEY') is None:
    load_dotenv()

class Assistent:

    def __init__(self):
        self.__client = anthropic.Anthropic()


    def __load_prompt(self, question : str ):
        return f"""
            You will receive the first 5 records of a pandas DataFrame along with the columns and their data types. Your task is to:

            Analyze these records to understand the structure, content, and data types within the DataFrame.

            Respond to a follow-up question, which may involve statistical summaries, data transformations, or visualizations.

            Provide:

            An executable Python function using pandas and seaborn that performs the requested analysis or visualization. The function should prioritize accuracy and correct handling of the data.
            Implement appropriate error handling to ensure the function's robustness, while balancing simplicity and thorough checks.
            If no specific chart type is requested, determine and suggest the most suitable visualization based on the data, analysis, and context.
            Apply seaborn styling options for a polished and well-formatted chart unless otherwise specified.
            Ensure the function returns the result so it can be displayed with Streamlit.
            Make the charts interactable using Plotly for enhanced user interaction.
            
            Importan : Include the necessary import statements within the function to ensure it runs independently.

            Return your response in the following format and with the same function name:

            def requested_function(df):
                # Your code here
                return fig

            Input Format:
            User Question : {question}
            First 5 Rows of DataFrame: {self.__df.head().to_dict(orient='records')}
            Columns and Data Types: : {self.__df.dtypes.to_dict()}
            The priority is to ensure the accuracy of the analysis, with a balanced approach to error-checking and code simplicity.

            No specific verbosity is required for the explanation text; provide clear and concise context as needed.
        """
    

    def __fetch_executale_code(self, prompt):

        # Retry logic with exponential backoff
        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):

            print(f"Attempt {attempt + 1} of {max_retries}...")

            try:
                message = self.__client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    temperature=0,
                    system="You are a world-class Data Engineer.",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                )

                return message.content[0].text.split("```python")[1].split("```")[0]
            
            except InternalServerError as e:
                
                print(e)

                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    st.warning(f"Server overloaded, retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    st.error("Failed to fetch executable code after multiple attempts.")
                    raise e
    
    def __process_question(self, question : str):
        prompt = self.__load_prompt(question)
        exec_code = self.__fetch_executale_code(prompt)
        local_vars = {}
        exec(exec_code, {}, local_vars)
        return local_vars.get('requested_function', lambda df: None)(self.__df)
    
    def make_alive(self):

        hide_streamlit_style = """
                    <style>
                        /* Hide the Streamlit header and menu */
                        header {visibility: hidden;}
                        /* Optionally, hide the footer */
                        .streamlit-footer {display: none;}
                        /* Hide your specific div class, replace class name with the one you identified */
                        .st-emotion-cache-uf99v8 {display: none;}
                    </style>
                    """

        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

        uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

        if uploaded_file is not None:

            self.__df = pd.read_csv(uploaded_file)

            # Automatically open the sidebar
            st.sidebar.markdown("## Columns and Data Types:")
            st.sidebar.write(self.__df.dtypes)

            # Streamlit chat interface
            if 'messages' not in st.session_state:
                st.session_state['messages'] = []

            st.title("Data Analysis Assistant")

            # Input box for user to type their question
            user_input = st.text_input("Ask a question about the dataset:", key="user_input")

            if st.button("Send", disabled=st.session_state.get('processing', False), key = "submit_button"):

                if user_input:

                    st.session_state['processing'] = True

                    with st.spinner('Processing your request... 🕒'):
                        try:
                            result = self.__process_question(user_input)
                            st.plotly_chart(result)
                        except Exception as e:
                            print(e)
                            return e
                        
                        st.session_state['processing'] = False
