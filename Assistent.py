

from anthropic import InternalServerError
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import anthropic
import time 
import os

import matplotlib
import seaborn
import pandas
import plotly
import statsmodels

if os.getenv('ANTHROPIC_API_KEY') is None:
    load_dotenv()

class Assistent:

    def __init__(self):

        if os.getenv('ANTHROPIC_API_KEY') is not None:
            self.__client = anthropic.Anthropic()

        elif os.getenv('OPENAI_API_KEY') is not None:
            self.__client = OpenAI()


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
                    Ensure the function returns a Plotly figure object so it can be displayed with Streamlit.
                    Make the charts interactable using Plotly for enhanced user interaction.
                    
                    Important: Include the necessary import statements within the function to ensure it runs independently.
                    Important: The function should always expect a DataFrame as input and return a Plotly figure object.

                    Return your response in the following format and with the same function name:

                    def requested_function(df):
                        # Your code here
                        return fig

                    These are the only imports allowed in the function:
                        import matplotlib
                        import seaborn
                        import pandas
                        import plotly
                        import statsmodels

                    All imports are already included in the initial code template. You can use any of these libraries to complete the task.

                    Input Format:
                    User Question : {question}
                    First 5 Rows of DataFrame: {self.__df.head().to_dict(orient='records')}
                    Columns and Data Types: : {self.__df.dtypes.to_dict()}
                    The priority is to ensure the accuracy of the analysis, with a balanced approach to error-checking and code simplicity.

                    No specific verbosity is required for the explanation text; provide clear and concise context as needed.
                """
    
    def __antrohic_api_call(self, prompt):
        message = self.__client.messages.create(
            model="claude-3-opus-20240229",
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

    def __openai_api_call(self, prompt):
        
        completion = self.__client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content.split("```python")[1].split("```")[0]

    def __fetch_executale_code(self, prompt):

        # Retry logic with exponential backoff

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):

            print(f"Attempt {attempt + 1} of {max_retries}...")

            try:

                if os.getenv('ANTHROPIC_API_KEY') is not None:
                    return self.__antrohic_api_call(prompt)
                
                if os.getenv('OPENAI_API_KEY') is not None:
                    return self.__openai_api_call(prompt)
                    
            
            except InternalServerError as e:
                
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

        return local_vars.get('requested_function', lambda df: None)(self.__df), exec_code
    
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

            self.__df = pandas.read_csv(uploaded_file)

            # Automatically open the sidebar
            st.sidebar.markdown("## Columns and Data Types:")
            st.sidebar.write(self.__df.dtypes)

            # Streamlit chat interface
            if 'messages' not in st.session_state:
                st.session_state['messages'] = []

            st.title("Data Analysis Assistant")

            # Input box for user to type their question
            user_input = st.text_input("Ask a question about the dataset:", key="user_input")

            if st.button("Send", disabled=st.session_state.get('processing', False), key="submit_button"):

                if user_input:

                    st.session_state['processing'] = True

                    start_time = time.time()

                    with st.spinner('Processing your request...'):
                        
                        try:

                            result, func = self.__process_question(user_input)

                            end_time = time.time()
                            processing_time = end_time - start_time
                            st.success(f"Request processed in {processing_time:.2f} seconds")
                            
                            with st.expander("Code used to generate the result"):
                                st.code(func, language='python')


                            st.plotly_chart(result)
                            st.session_state['messages'].append({"role": "user", "content": user_input})
                            st.session_state['messages'].append({"role": "assistant", "content": func})
                            
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                        
                        st.session_state['processing'] = False
