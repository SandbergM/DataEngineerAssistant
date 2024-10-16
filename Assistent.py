from dotenv import load_dotenv
load_dotenv()

import gradio as gr
import pandas as pd

from OpenAiRequester import OpenAiRequester
from CodeRunner import CodeRunner
from Prompt import Prompt
import time


class Assistent:

    def __init__(self):

        self.__df = pd.DataFrame()
        self.__css = """
        #chart_row {
            height: 75vh!important;
        }
        #chart_output {
            height: 30em!important;
        }
        #data_types_row {
            height: 75vh!important;
        }
        #data_types {
            height: 75vh!important;
        }
        """


    def __handle_input(self, user_input, total_cost : float = 0.0, retries : int = 5):
            
            total_cost += total_cost

            try:

                prompt_str = Prompt().get_prompt(user_input, self.__df)

                open_ai_time = time.time()
                result = OpenAiRequester(prompt_str).call_openai_with_retries()
                
                total_cost += result["cost"]

                open_ai_time = time.time() - open_ai_time

                execution_time = time.time()
                code_results = CodeRunner(result["function_str"], self.__df).run_code()
                execution_time = time.time() - execution_time
                
                open_ai_time_formatted = time.strftime("%H:%M:%S", time.gmtime(open_ai_time))
                execution_time_formatted = time.strftime("%H:%M:%S", time.gmtime(execution_time))
                peak_memory_mb = code_results["peak_memory"] / (1024 * 1024)

                return (
                    code_results["result"],
                    result["function_str"],
                    result["message"],
                    f"${result['cost'] + total_cost:.6f} USD",
                    open_ai_time_formatted,
                    execution_time_formatted,
                    f"{peak_memory_mb:.2f} MB",
                    code_results["message"]
                )
            
            except Exception as e:

                print(f"{__name__} Error occurred: retrying {retries} more times.")
                
                if retries > 0:
                    return self.__handle_input(user_input, total_cost, retries - 1)
                else:
                    return (None, None, None, None, None, None, None, str(e))

    def make_alive(self):

        with gr.Blocks(css = self.__css) as demo:
        
            with gr.Row(elem_id="chart_row"):

                with gr.Column(scale = 3):
                    message_output = gr.Textbox(label="Message", interactive=False)
                    chart_output = gr.Plot(label="Generated Chart", elem_id="chart_output")
                    user_input = gr.Textbox(label="Enter your input here")
                    submit_button = gr.Button("Submit")

                with gr.Column(scale = 1, elem_id="data_types_row"):
                    file_upload = gr.File(label="Upload a CSV file")
                    data_types_output = gr.JSON(label="Columns and Data Types", elem_id="data_types")

                    def update_data_types(file):
                        if file is not None:
                            self.__df = pd.read_csv(file.name)
                            return self.__df.dtypes.apply(lambda x: x.name).to_dict()
                        return {}

                    file_upload.change(
                        update_data_types, 
                        inputs=file_upload, 
                        outputs=data_types_output
                    )

            with gr.Row():
                cost_output = gr.Textbox(label="Cost", interactive=False)
                open_ai_time_output = gr.Textbox(label="OpenAI Time", interactive=False)
                execution_time_output = gr.Textbox(label="Execution Time", interactive=False)
                peak_memory_output = gr.Textbox(label="Memory Usage", interactive=False)

            with gr.Row():
                with gr.Accordion("Function generated", open=False):
                    function_str_output = gr.Code(interactive=False, language="python")

            submit_button.click(
                self.__handle_input, 
                inputs=user_input, 
                outputs=[
                    chart_output, 
                    function_str_output, 
                    message_output, 
                    cost_output, 
                    open_ai_time_output, 
                    execution_time_output,
                    peak_memory_output,
                    message_output,
                ]
            )



        demo.launch()