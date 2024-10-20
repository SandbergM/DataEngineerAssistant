import sqlite3
import pandas as pd
from app.core.OpenAiRequester import OpenAiRequester
import os
from app.core.utils import scramble_dataframe


class Db:

    def __init__(self):
        self.__db_path = f"database.sqlite"
        self.__open_ai_requester = OpenAiRequester()
        self.__create_database_if_not_exists()

    def __create_database_if_not_exists(self):
        if not os.path.exists(self.__db_path):
            conn = self.connect()
            conn.close()

    def connect(self):
        return sqlite3.connect(self.__db_path)

    def create_table(self, table_name: str, df: pd.DataFrame):
        drop_statement, create_statement = self.__get_create_statement(table_name, df)
        conn = self.connect()
        conn.execute(drop_statement)
        conn.execute(create_statement)
        conn.close()

    def __get_create_statement(self, table_name: str, df: pd.DataFrame):

        df = scramble_dataframe(df)

        prompt = f"""

            You will receive the first 5 records of a pandas DataFrame along with the columns and their data types. Your task is to:
            Analyze these records to understand the structure, content, and data types within the DataFrame.
            Generate a create table statement for the given DataFrame for a sqlite3 database.

            Return your response in the following format:

            ```sql_drop_start
            DROP TABLE IF EXISTS "{table_name}";
            ```sql_drop_end

            ```sql_create_start
            CREATE TABLE "{table_name}" (

            );
            ```sql_create_end

            First 5 Rows of DataFrame: {df.head().to_dict(orient='records')}
            Columns and Data Types: : {df.dtypes.to_dict()}

        """

        result = self.__open_ai_requester.call_openai(prompt)

        return (
            result.get("completion")
            .choices[0]
            .message.content.split("```sql_drop_start")[1]
            .split("```sql_drop_end")[0],
            result.get("completion")
            .choices[0]
            .message.content.split("```sql_create_start")[1]
            .split("```sql_create_end")[0],
        )

    def insert_data(self, table_name: str, df: pd.DataFrame):
        conn = self.connect()
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()

    def get_table_schema(self, table_name: str) -> str:

        conn = self.connect()
        cursor = conn.cursor()

        # Query the sqlite_master table to get the CREATE TABLE statement
        cursor.execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        )

        create_statement = cursor.fetchone()

        conn.close()

        if create_statement:
            return create_statement[0][len("CREATE TABLE ") :]
        else:
            return f"Table '{table_name}' does not exist."

    def get_table_head(self, table_name: str) -> pd.DataFrame:

        conn = self.connect()
        df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5;", conn)
        conn.close()

        return scramble_dataframe(df).head().to_dict(orient="records")

    def execute_query(self, sql_query: str) -> pd.DataFrame:

        conn = self.connect()
        df = pd.read_sql(sql_query, conn)
        conn.close()

        return df
