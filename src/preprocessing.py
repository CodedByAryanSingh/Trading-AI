import pandas as pd


class DataPreprocessor:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def preprocess(self) -> pd.DataFrame:
        # Remove rows containing missing values
        self.data.dropna(inplace=True)

        # Reset row index
        self.data.reset_index(inplace=True, drop=True)

        return self.data