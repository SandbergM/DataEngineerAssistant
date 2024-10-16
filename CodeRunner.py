
import tracemalloc

class CodeRunner:

    def __init__(self, code_str, input_df):
        self.__code = code_str
        self.__df = input_df


    def run_code(self):
        """
        Runs the code provided during the initialization of the CodeRunner instance.
        
        This method attempts to execute the provided code string and captures the result and peak memory usage.
        If an exception occurs during execution, it captures the exception message.
        
        Returns:
            dict: A dictionary containing:
                - 'failed' (bool): Indicates whether the code execution failed.
                - 'result' (any): The result of the executed code's 'requested_function'.
                - 'peak_memory' (int): The peak memory usage during the code execution in bytes.
                - 'message' (str): A message indicating the status of the execution or the exception message if failed.
        """
        
        result = None
        peak_memory = None
        message = "Ok"
        failed = False
        
        try:
            # Attempt to execute the provided code and capture the result and peak memory usage
            result, peak_memory = self.__execute_code(self.__code)
        except Exception as e:
            # If an exception occurs, capture the exception message
            message = str(e)
            failed = True

        # Return a dictionary with the execution details
        return {
            'failed': failed,
            'result': result, 
            'peak_memory': peak_memory,
            'message': message
        }
    
    def __execute_code(self, code_str : str) -> tuple:

        """
        Executes a given code string in a local context and retrieves the result from a specified function.
        This method starts memory tracking, executes the provided code string, and then retrieves the result
        from a function named 'requested_function' within the executed code. It also measures the peak memory
        usage during the execution.
        Args:
            code_str (str): The code string to be executed. It should define a function named 'requested_function'
                            that takes a DataFrame as an argument.
        Returns:
            tuple: A tuple containing:
                - The result of the 'requested_function' when applied to the instance's DataFrame.
                - The peak memory usage during the execution in bytes.
        """

        local_vars = {}
        tracemalloc.start()
        exec(code_str, {}, local_vars)
        result_function = local_vars.get('requested_function', lambda df: None)
        res = result_function(self.__df)
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return res, peak_memory