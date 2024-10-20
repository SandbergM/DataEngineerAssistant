import pandas as pd


def scramble_dataframe(df: pd.DataFrame, scrambles=10) -> pd.DataFrame:
    """
    Scrambles (shuffles) all the rows in a pandas DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to scramble.

    Returns:
    pd.DataFrame: The scrambled DataFrame.
    """

    scrambled_df = df.sample(frac=1).reset_index(drop=True)

    for _ in range(scrambles):
        scrambled_df = scrambled_df.sample(frac=1).reset_index(drop=True)

    return scrambled_df
