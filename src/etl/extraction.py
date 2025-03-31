import pandas as pd


class DataExtractor:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def extract_data(self) -> pd.DataFrame:
        """
        Reads the CSV file and extracts the raw data into a DataFrame.

        :return: Pandas DataFrame containing raw data
        """
        try:
            # Load the CSV file into a DataFrame
            data = pd.read_csv(self.file_path)
            return data
        except Exception as e:
            print(f"Error reading the file: {e}")
            # Return an empty DataFrame in case of an error
            return pd.DataFrame()