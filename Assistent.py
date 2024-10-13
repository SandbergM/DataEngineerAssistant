from anthropic import InternalServerError
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import time 
import os

import matplotlib
import seaborn
import pandas
import plotly
import statsmodels
import gradio as gr
import tracemalloc

if os.getenv('ANTHROPIC_API_KEY') is None:
    load_dotenv()

class Assistent:

    def __init__(self):

        self.__df = pandas.read_csv("./data/Crime_Data_from_2020_to_Present.csv")

        if os.getenv('ANTHROPIC_API_KEY') is not None:
            self.__client = anthropic.Anthropic()

        if os.getenv('OPENAI_API_KEY') is not None:
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
Important: I want the fig to be in dark mode.
Important: the function should be named requested_function.

Return your response in the following format and with the same function name:

```python
def requested_function(df):
    # Your code here
    return fig
```

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

        def calculate_chatgpt_cost(total_tokens, rate_per_token):
            """
            Calculate the total cost of a ChatGPT API call in USD.

            :param total_tokens: Total number of tokens used in the API call (completion + prompt).
            :param rate_per_token: Cost per token in USD.
            :return: Total cost in USD.
            """
            total_cost = total_tokens * rate_per_token
            return total_cost
        
        completion = self.__client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content.split("```python")[1].split("```")[0], calculate_chatgpt_cost(completion.usage.total_tokens, 0.00000015)
    
    
    def __fetch_executale_code(self, prompt):

        # Retry logic with exponential backoff

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):

            print(f"Attempt {attempt + 1} of {max_retries}...")

            try:

                

                if os.getenv('ANTHROPIC_API_KEY') is not None:
                    return self.__antrohic_api_call(prompt)
                
                elif os.getenv('OPENAI_API_KEY') is not None:
                    return self.__openai_api_call(prompt)
                
                else:
                    raise ValueError("No valid API key found.")

            
            except InternalServerError as e:
                
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    print(f"Server overloaded, retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

                else:
                    print("Failed to fetch executable code after multiple attempts.")
                    raise e
    
    def __process_question(self, question : str):

        prompt = self.__load_prompt(question)
        exec_code, usd_cost = self.__fetch_executale_code(prompt)
        local_vars = {}


        exec(exec_code, {}, local_vars)
        tracemalloc.start()
        res = local_vars.get('requested_function', lambda df: None)(self.__df)
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()


        return res, exec_code, peak_memory, usd_cost
    
    def make_alive(self):

        def handle_question(question):

            try:
                return self.__process_question(question)
            
            except Exception as e:
                return None, f"An error occurred: {e}", 0, 0
        

        with gr.Blocks(fill_height=True) as demo:

            with gr.Group():

                with gr.Accordion("Columns and Data Types", open=False):
                    gr.JSON(value=self.__df.dtypes.apply(lambda x: x.name).to_dict(), label="Columns and Data Types")

                with gr.Row():
                    question_input = gr.Textbox(label="Question", placeholder="Ask a question about the dataset", lines=1)
                    
                result_output = gr.Plot(label="Result")

                with gr.Accordion("Generated Code", open=False):
                    code_output = gr.Code(label="Generated Code", language="python")

                with gr.Accordion("Processing details", open=False):
                    peak_memory_output = gr.Textbox(label="Peak Memory Usage (MB)", interactive=False)
                    usd_cost_output = gr.Textbox(label="Cost (USD)", interactive=False)
                    elapsed_time_output = gr.Textbox(label="Elapsed Time (seconds)", interactive=False)
                

                def handle_question_with_timing(question):
                    start_time = time.time()
                    result, code, peak_memory, usd_cost = handle_question(question)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    return result, code, peak_memory, usd_cost, elapsed_time

                question_input.submit(fn=handle_question_with_timing, inputs=question_input, outputs=[result_output, code_output, peak_memory_output, usd_cost_output, elapsed_time_output])

        demo.launch()