import pandas as pd
from filter import Filter
import numpy as np
from sklearn.preprocessing import MinMaxScaler


class Drop_diff_values(Filter):
    """Drop_diff_values removes features that require further processing before they can be used"""

    def __call__(self, data):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable.

        Args:
            data (_type_): _description_ the data to be altered

        Returns:
            _type_:? _description_ the altered data
        """

        data_altered = data.drop(["portId", "etaRaw"], axis=1)
        return data_altered


class Normalizer(Filter):
    """Normalizer normalizes values"""

    def __call__(self, data):
        """_summary_ use MinMaxScaler to normalize the data

        Args:
            data (_type_): _description_ the data to be normalized

        Returns:
            _type_:? _description_ the normalized data
        """
        scaler = MinMaxScaler()
        time_scaler = MinMaxScaler()
        time_scaler.fit(data["time_diff"].values.reshape(-1, 1))

        data_normalized = data.drop(["vesselId", "time", "time_diff"], axis=1)
        data_normalized = pd.DataFrame(
            scaler.fit_transform(data_normalized),
            columns=data_normalized.columns,
            index=data_normalized.index,
        )

        data_normalized["vesselId"] = data["vesselId"]
        data_normalized["time"] = data["time"]
        data_normalized["time_diff"] = data["time_diff"]

        return data_normalized, time_scaler


class Sort_by_id(Filter):
    """Sort_by_id is a filter class that sorts the data by id"""

    def __call__(self, data):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable.

        Args:
            data (_type_): _description_ the data to be sorted

        Returns:
            _type_:? _description_ the sorted data
        """

        data_grouped = data.groupby("vesselId").agg(lambda x: list(x))
        data_grouped = data_grouped.reset_index(inplace=True)
        print(data_grouped.columns)
        return data_grouped


class Create_sequence_vectors(Filter):
    """zips all features into a sequence vector"""

    def __call__(self, data):
        """_summary_ zips all features into sequence vectors over all timestamps for each vessel.

        Args:
            data (_type_): _description_ the data to be zipped

        Returns:
            _type_:? _description_ the zipped data
        """

        def zip_features(group):
            features = [
                list(feature_tuple)
                for feature_tuple in zip(
                    group["time"],
                    group["cog"],
                    group["rot"],
                    group["heading"],
                    group["navstat"],
                    group["latitude"],
                    group["longitude"],
                    group["time_diff"],
                )
            ]
            return features

        data_zipped = (
            data.groupby("vesselId")
            .apply(zip_features)
            .to_frame()
            .rename(columns={0: "sequences"})
        )

        return data_zipped


class Timestamp_to_timedif(Filter):
    """Timestamp_to_timedif is a filter class that calculates the time difference between two consecutive timestamps"""

    def __call__(self, data):
        """_summary_ sets the time data to the timedifference from last entry.

        Args:
            data (_type_): _description_ the data to be altered

        Returns:
            _type_:? _description_ the altered data
        """

        data["time"] = data["time"].apply(lambda x: pd.Series(x))
        data["time"] = data["time"]
        data["time_diff"] = data.groupby("vesselId")["time"].diff(-1).dt.total_seconds()
        data["time_diff"] = data["time_diff"].abs().fillna(0)
        # data = data.drop("time", axis=1) # Needs the actual dates for creating timesteps during training data generation, and querying
        return data
