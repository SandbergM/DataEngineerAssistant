from openai import OpenAI
import time


class OpenAiRequester:
    def __init__(self, prompt):
        self.__client = OpenAI()
        self.__prompt = prompt
        self.__max_retries=5


    def __calculate_chatgpt_cost(self, total_tokens, rate_per_token):
        """
        Calculate the total cost of a ChatGPT API call in USD.

        :param total_tokens: Total number of tokens used in the API call (completion + prompt).
        :param rate_per_token: Cost per token in USD.
        :return: Total cost in USD.
        """
        total_cost = total_tokens * rate_per_token
        return total_cost
    
    def __call_openai(self):
        
        completion = self.__client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": self.__prompt}
            ]
        )

        return {
            "cost" : self.__calculate_chatgpt_cost(completion.usage.total_tokens, 0.00000015),
            "function_str" : self.__parse_function(completion=completion),
            "message" : self.__parse_message(completion=completion)
        }
    
    def __parse_function(self, completion):
        """
        Parse the function string and return the function object.

        :param function_str: The string representation of the function.
        :return: The function object.
        """
        try:
            return completion.choices[0].message.content.split("```function_start")[1].split("```function_end")[0]
        except Exception as e:
            print(e)
            raise Exception("Failed to parse the function string.")

    def __parse_message(self, completion):
        """
        Parse the message string and return the message.

        :param message_str: The string representation of the message.
        :return: The message.
        """
        try:
            return completion.choices[0].message.content.split("```message_start")[1].split("```message_end")[0]
        except Exception as e:
            print(e)
            raise Exception("Failed to parse the message string.")

    def call_openai_with_retries(self):
        """
        Call the OpenAI API with retries in case of failure.

        :param prompt: The prompt to send to the OpenAI API.
        :param max_retries: Maximum number of retry attempts.
        :return: The response from the OpenAI API.
        :raises Exception: If the maximum number of retries is reached without success.
        """
        attempts = 0
        
        while attempts < self.__max_retries:
            try:

                print(f"{__name__} Attempt {attempts + 1} of {self.__max_retries}")
                return self.__call_openai()
            
            except Exception as e:

                attempts += 1
                print(f"{__name__} Attempt {attempts} failed: {e}")
                if attempts == self.__max_retries:
                    print(f"{__name__} Max retries reached. Raising exception.")
                    raise e
                
                print(f"{__name__} Retrying in {2 ** attempts} seconds...")
                time.sleep(2 ** attempts)  # Exponential backoff