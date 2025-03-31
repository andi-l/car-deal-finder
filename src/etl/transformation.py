import pandas as pd
import numpy as np


class DataTransformer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def clean_price(self
                    ,price: str
                    ) -> float:
        """
        Cleans and converts the price field from a string to a float.

        :param price: string
        :return: Numeric price as float
        """
        if pd.isna(price):
            return np.nan  # Handle missing values

        try:
            price = price.replace("₹", "").replace(",", "").strip()
            return float(price)
        except (ValueError, TypeError):
            return np.nan

    def clean_km(self
                 ,kilometer: str
                 ) -> float:
        """
        Cleans and converts the kilometer driven field from a string to a float.

        :param kilometer: string
        :return: Numeric kilometers as float
        """
        if pd.isna(kilometer):
            return np.nan  # Handle missing values

        try:
            kilometer = kilometer.replace("km", "").replace(",", "").strip()
            return float(kilometer)
        except (ValueError, TypeError):
            return np.nan

    def update_car_age(self) -> None:
        """
            Calculate the age of the car based on the current year.
        """
        current_year = pd.Timestamp.now().year
        self.df["Age"] = current_year - self.df["Year"]

    def calculate_price_per_km(self,
                               row
                               ) -> float:
        """
        Calculate price per kilometer ratio for a vehicle.

        :param row: pandas Series containing vehicle data
        :return: Price/km ratio as float, -1 for invalid inputs, np.nan for errors
        """
        price = row["AskPrice"]
        kilometer = row["kmDriven"]

        if pd.isna(price) or pd.isna(kilometer):
            return np.nan

        try:
            if kilometer > 0:
                return price / kilometer
            else:
                return -1
        except (ValueError, TypeError, ZeroDivisionError):
            return np.nan

    def create_brand_model_column(self):
        """
            Combines brand and model columns into a single column.
        """
        # cleaning model column
        self.df["model"] = self.df["model"].str.strip()  # Remove extra spaces
        self.df["model"] = self.df["model"].str.replace(" ", "-")  # Replace blank spaces
        self.df["model"] = self.df["model"].str.lower()  # Convert to lowercase
        self.df["Brand_Model"] = self.df["Brand"] + " " + self.df["model"]

    def calculate_relative_price(self) -> None:
        """
            Calculate the price per kilometer relative to the brand_model average price per kilometer.

            Exclude rows with PricePerKm == -1 (new cars with insufficient data)
        """
        # exclude rows with PricePerKm == -1 from the calculation because they are new cars
        # not enough data and priceperkm calculation doesnt work
        valid_rows = self.df["PricePerKm"] != -1

        # calculate the mean PricePerKm for each Brand_Model combo
        self.df.loc[valid_rows, "PricePerKM_mean"] = self.df.groupby("Brand_Model")["PricePerKm"].transform("mean")

        # Calculate the relative price PricePerKm/PricePerKM_mean
        # RelativePrice == 1 means the car is priced at the average.
        # RelativePrice > 1 indicates the car is more expensive than average.
        # RelativePrice < 1 indicates the car is cheaper than average.
        self.df.loc[valid_rows, "RelativePrice"] = self.df["PricePerKm"] / self.df["PricePerKM_mean"]

        # Assign -1 to RelativePrice for invalid rows with PricePerKm == -1
        self.df.loc[~valid_rows, "RelativePrice"] = -1

    def classify_relative_price(self
                                , relative_price: float
                                ) -> str:
        """
        Classify the relative price of a car based on thresholds defined in dictionary.

        :param relative_price: float representing the relative price
        :return: str classification of the cars price
        """

        # thresholds and corresponding labels
        classifications = {
            "Very Cheap": (0, 0.5),
            "Cheap": (0.5, 0.9),
            "Average": (0.9, 1.1),
            "Expensive": (1.1, 2.0),
            "Very Expensive": (2.0, float('inf'))
        }

        # Check which classification the relative price falls into
        for label, (lower, upper) in classifications.items():
            if lower <= relative_price < upper:
                return label
        return "Unknown"  # if no match

    def transform_data(self) -> pd.DataFrame:
        """
        Apply all transformation functions and return processed DataFrame.

        :return: processed DataFrame
        """
        #Applying transformation functions
        self.df["AskPrice"] = self.df["AskPrice"].apply(self.clean_price)
        self.df["kmDriven"] = self.df["kmDriven"].apply(self.clean_km)
        self.df["PricePerKm"] = self.df.apply(self.calculate_price_per_km, axis=1)

        self.update_car_age()
        self.create_brand_model_column()
        self.calculate_relative_price()
        self.df["PriceClassification"] = self.df["RelativePrice"].apply(
            self.classify_relative_price)

        self.df.columns = self.df.columns.str.lower()

        # Exclude rows with NULL and 0 in kmDriven
        # using copy to work with a real copy not only a view of original
        self.df = self.df[self.df["priceclassification"] != "Unknown"].copy()

        return self.df
