class Prompt:
    
    def get_prompt(self, question : str, df) -> str:
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
        First 5 Rows of DataFrame: {df.head().to_dict(orient='records')}
        Columns and Data Types: : {df.dtypes.to_dict()}

        """