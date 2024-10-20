from app.core.OpenAiRequester import OpenAiRequester
from app.core.utils import scramble_dataframe


class Prompt:

    def __init__(self):
        self.__openai_requester = OpenAiRequester()

    def get_db_query(self, question: str, table_details: str, df) -> str:

        prompt = f"""
        Given the following details about a table and the user's request, generate a SELECT query for SQLite3 that extracts the data needed to process the users request. 
        The SELECT query should not include any aggregations or transformations.
        
        Table Details:{table_details}
        User Request: {question}
        Generate an accurate SQLite3 SELECT statement based on the user's requirements and the provided table structure."
        Return in the format: 
        ```sql_start
            Select query here
        ```sql_end
        """

        query = self.__openai_requester.call_openai(prompt=prompt)
        return (
            query.get("completion")
            .choices[0]
            .message.content.split("```sql_start")[1]
            .split("```sql_end")[0]
            .strip()
        )

    def get_code_prompt(self, question: str, df) -> str:

        __df = scramble_dataframe(df)
        __head = __df.head(10).to_dict(orient="records")

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

        Important: The function should always expect a DataFrame as input and return a Plotly figure object.
        Important: Include the necessary import statements within the function to ensure it runs independently.
        Important: the function should be named requested_function.
        Important: The charts should be interactive using Plotly and in darkmode.
        Return your response in the following format and with the same function name:


        ```function_start
        def requested_function(df):
            # Your code here
            return fig
        ```function_end

        ```message_start
        Friendly message to the user
        ``´message_end


        These are the only imports allowed in the function:
        Important : They are already included in the initial code template. You can use any of these libraries to complete the task without importing them again.
            import matplotlib
            import seaborn
            import pandas
            import plotly
            import statsmodels
            import gradio as gr
            import tracemalloc
            import pandas as pd
            import numpy as np

        Input Format:
        User Question : {question}
        First 5 Rows of DataFrame: {__head}
        Columns and Data Types: : {df.dtypes.to_dict()}

        """
