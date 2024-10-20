import pandas as pd

from app.core.OpenAiRequester import OpenAiRequester
from CodeRunner import CodeRunner
from app.core.Prompt import Prompt
import time


class Assistent:

    def __init__(self):

        self.__df = pd.DataFrame()

    def __handle_input(self, user_input, total_cost: float = 0.0, retries: int = 5):

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

            open_ai_time_formatted = time.strftime(
                "%H:%M:%S", time.gmtime(open_ai_time)
            )
            execution_time_formatted = time.strftime(
                "%H:%M:%S", time.gmtime(execution_time)
            )
            peak_memory_mb = code_results["peak_memory"] / (1024 * 1024)

            return (
                code_results["result"],
                result["function_str"],
                result["message"],
                f"${result['cost'] + total_cost:.6f} USD",
                open_ai_time_formatted,
                execution_time_formatted,
                f"{peak_memory_mb:.2f} MB",
                code_results["message"],
            )

        except Exception as e:

            print(f"{__name__} Error occurred: retrying {retries} more times.")

            if retries > 0:
                return self.__handle_input(user_input, total_cost, retries - 1)
            else:
                return (None, None, None, None, None, None, None, str(e))
