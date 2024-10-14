import pandas as pd
import numpy as np
from datetime import datetime
# from geopy.distance import geodesic
from typing import Tuple, List
from autogluon.tabular import TabularDataset


class AISFeatureEngineer:
    """
    Class for performing feature engineering on 
    AIS data for vessel position prediction.
    """

    def __init__(self,
                 ais_train_path: str, 
                 ais_test_path: str,
                 vessels_path: str = None,
                 schedules_path: str = None, ports_path: str = None
                 ):
        """
        Initializes the AISFeatureEngineer with paths to the datasets.

        Args:
            ais_train_path (str): Path to the AIS training data CSV file.
            ais_test_path (str): Path to the AIS testing data CSV file.
            vessels_path (str, optional): Path to the vessels data CSV file.
            schedules_path (str, optional): Path to the schedules data CSV.
            ports_path (str, optional): Path to the ports data CSV file.
        """
        self.ais_train_path = ais_train_path
        self.ais_test_path = ais_test_path
        self.vessels_path = vessels_path
        self.schedules_path = schedules_path
        self.ports_path = ports_path

        self.ais_train_df = None
        self.ais_test_df = None
        self.vessels_df = None
        self.schedules_df = None
        self.ports_df = None

    def load_data(self) -> None:
        """
        Loads the datasets into pandas DataFrames.
        """
        self.ais_train_df = pd.read_csv(self.ais_train_path)
        self.ais_test_df = pd.read_csv(self.ais_test_path)
        if self.vessels_path:
            self.vessels_df = pd.read_csv(self.vessels_path)
        if self.schedules_path:
            self.schedules_df = pd.read_csv(self.schedules_path)
        if self.ports_path:
            self.ports_df = pd.read_csv(self.ports_path)

    def preprocess_ais_data(self) -> None:
        """
        Preprocesses the AIS data by parsing dates and handling missing values.
        """
        self.ais_train_df['time'] = pd.to_datetime(self.ais_train_df['time'])
        self.ais_test_df['time'] = pd.to_datetime(self.ais_test_df['time'])

        self.ais_train_df.fillna(method='ffill', inplace=True)
        self.ais_test_df.fillna(method='ffill', inplace=True)

        if self.vessels_df is not None:
            self.ais_train_df = pd.merge(
                self.ais_train_df, 
                self.vessels_df, on='vesselId', how='left'
                )
            self.ais_test_df = pd.merge(
                self.ais_test_df, 
                self.vessels_df, 
                on='vesselId', 
                how='left'
                )

        self.ais_train_df.reset_index(drop=True, inplace=True)
        self.ais_test_df.reset_index(drop=True, inplace=True)

    def generate_features(self) -> None:
        """
        Generates features for the AIS data.
        """
        self.ais_train_df = self._generate_features_for_df(
            self.ais_train_df,  
            is_test=False
            )
        self.ais_test_df = self._generate_features_for_df(
            self.ais_test_df, 
            is_test=True
            )

    def _generate_features_for_df(self, 
                                  df: pd.DataFrame, 
                                  is_test: bool = False
                                  ) -> pd.DataFrame:
        """
        Generates features for a given AIS DataFrame.

        Args:
            df (pd.DataFrame): The AIS DataFrame.
            is_test (bool): Flag indicating whether the DataFrame is test data.

        Returns:
            pd.DataFrame: The DataFrame with new features.
        """
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek
        df['month'] = df['time'].dt.month
        df['day_of_month'] = df['time'].dt.day

        df = self._process_etaRaw(df)

        categorical_cols = ['navstat', 'vesselType', 'homePort']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')

        df.fillna(0, inplace=True)

        return df

    def _process_etaRaw(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the 'etaRaw' column to compute time difference to ETA.

        Args:
            df (pd.DataFrame): The AIS DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with 'eta_timedelta' feature.
        """
        def parse_eta(row):
            eta_str = row['etaRaw']
            try:
                eta_datetime = datetime.strptime(eta_str, '%m-%d %H:%M')
                # Replace year with current year or next year -
                #  if date has passed
                # TODO: is this necessary?
                eta_datetime = eta_datetime.replace(year=row['time'].year)
                if eta_datetime < row['time']:
                    eta_datetime = eta_datetime.replace(
                        year=row['time'].year + 1)
                return (eta_datetime - row['time']).total_seconds()
            except Exception:
                return np.nan

        df['eta_timedelta'] = df.apply(parse_eta, axis=1)
        df['eta_timedelta'].fillna(0, inplace=True)
        return df

    def prepare_data_for_modeling(self) -> Tuple[
            pd.DataFrame, 
            pd.DataFrame, 
            List[str], 
            str, 
            str
    ]:
        """
        Prepares the data for modeling with AutoGluon.

        Returns:
            Tuple containing training DataFrame, test DataFrame, 
            feature list, target latitude, and target longitude.
        """
        features = [col for col in self.ais_train_df.columns if col not in [
            'latitude', 'longitude', 'time', 'vesselId', 'portId', 'etaRaw']]
        target_lat = 'latitude'
        target_lon = 'longitude'

        train_df = self.ais_train_df.copy()
        test_df = self.ais_test_df.copy()

        return train_df, test_df, features, target_lat, target_lon


if __name__ == "__main__":
    feature_engineer = AISFeatureEngineer(
        ais_train_path='ais_train.csv',
        ais_test_path='ais_test.csv',
        vessels_path='vessels.csv',
        schedules_path='schedules_to_may_2024.csv',
        ports_path='ports.csv'
    )

    feature_engineer.load_data()

    feature_engineer.preprocess_ais_data()

    feature_engineer.generate_features()

    train_df, test_df, features, target_lat, target_lon = \
        feature_engineer.prepare_data_for_modeling()

    train_data = TabularDataset(train_df[features + [target_lat, target_lon]])
    test_data = TabularDataset(test_df[features])

    print("Training Data:")
    print(train_data.head())
    print("\nTest Data:")
    print(test_data.head())
