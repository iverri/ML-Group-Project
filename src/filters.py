from abc import ABC, abstractmethod
from pandas import DataFrame
import numpy as np
import h2o
import os
import pandas as pd
import math


class Filter(ABC):
    """
    Filter is an abstract class that defines the interface for all filters

    Args:
        ABC (_type_): _description_ abstract class/ interface
    """
    @abstractmethod
    def __call__(self):
        """
        _summary_ apply the preprocessing filter to the data,
        so that the filter is callable. 

        Args:
            
        """
        pass
    

class HandleMissingValues(Filter):
   
    def __call__(self, data) -> DataFrame:
        
        data.loc[data["cog"] >= 360, "cog"] = np.nan
        data.loc[data["sog"] >= 1023, "sog"] = np.nan
        data.loc[data["rot"] == -128, "rot"] = np.nan
        data.loc[data["heading"] == 511, "heading"] = (
            np.nan
        )
        pattern = r"^\d{2}-\d{2} \d{2}:\d{2}$"
        data["etaRaw"] = data["etaRaw"].where(
            data["etaRaw"].str.match(pattern, na=False), np.nan
        )
        return data
    

class GroupBy(Filter):
    """_summary_ GroupBy is a filter that groups the data by a collumn

    Args:
        data (DataFrame): _description_
        collumn (str): _description_

    Returns:
        DataFrame: _description_
    """

    def __call__(self, data: DataFrame, collumn: str) -> DataFrame:
        train_data_preprocessed = (
            data.groupby(collumn)
            .apply(lambda group: group.ffill().bfill())
            .reset_index(drop=True)
        )
        return train_data_preprocessed


class CalculateSeconds:
    """
    _summary_ CalculateSeconds is a filter that 
    calculates the seconds to ETA

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    def __call__(self, data) -> DataFrame:
        # Replace '00-' in etaRaw with the corresponding 
        # month and day from the 'time' column
        data["etaRaw"] = data["etaRaw"].mask(
            data["etaRaw"].str.contains("00-", na=False),
            "01" + data["etaRaw"].str[2:],
        )

        data["etaRaw"] = data["etaRaw"].mask(
            data["etaRaw"].str.contains("-00", na=False),
            data["etaRaw"].str[:2]
            + "-01"
            + data["etaRaw"].str[5:],
        )

        data["etaRaw"] = data["etaRaw"].mask(
            data["etaRaw"].str.contains(":60", na=False),
            data["etaRaw"].str[:9] + "59",
        )

        data["etaRaw"] = data["etaRaw"].mask(
            data["etaRaw"].str.contains("60:", na=False),
            data["etaRaw"].str[:6] + "01:00",
        )

        data["etaRaw"] = data["etaRaw"].mask(
            data["etaRaw"].str.contains("24:", na=False),
            data["etaRaw"].str[:6] + "23:59",
        )

        data["etaRaw"] = pd.to_datetime(
            data["time"].dt.year.astype(str)
            + "-"
            + data["etaRaw"]
            + ":00",
            format="%Y-%m-%d %H:%M:%S",
        )

        data["seconds_to_eta"] = (
            data["etaRaw"] - data["time"]
        ).dt.total_seconds()

        data = data.drop(columns=["etaRaw"])

        return data
        
        
class ConvertToTrigonometric:
    """
    _summary_ ConvertToTrigonometric is a filter that 
    converts the heading and other values to trigonometric coordinates

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    def __call__(self, data) -> DataFrame:
    
        train_latitude_radians = np.deg2rad(data["latitude"])
        train_longitude_radians = np.deg2rad(data["longitude"])
        train_cog_radians = np.deg2rad(data["cog"])
        train_heading_radians = np.deg2rad(data["heading"])
        train_hour = np.deg2rad(data["time"].dt.hour * 360 / 24)
        train_day = np.deg2rad(data["time"].dt.day * 360 / 30)
        train_month = np.deg2rad(data["time"].dt.month * 360 / 12)

        train_latitude_sin = np.sin(train_latitude_radians)
        train_latitude_cos = np.cos(train_latitude_radians)

        train_longitude_sin = np.sin(train_longitude_radians)
        train_longitude_cos = np.cos(train_longitude_radians)

        train_cog_sin = np.sin(train_cog_radians)
        train_cog_cos = np.cos(train_cog_radians)

        train_heading_sin = np.sin(train_heading_radians)
        train_heading_cos = np.cos(train_heading_radians)

        train_hour_sin = np.sin(train_hour)
        train_hour_cos = np.cos(train_hour)

        train_day_sin = np.sin(train_day)
        train_day_cos = np.cos(train_day)

        train_month_sin = np.sin(train_month)
        train_month_cos = np.cos(train_month)

        data["latitude_sin"] = train_latitude_sin
        data["latitude_cos"] = train_latitude_cos
        data["longitude_sin"] = train_longitude_sin
        data["longitude_cos"] = train_longitude_cos
        data["cog_sin"] = train_cog_sin
        data["cog_cos"] = train_cog_cos
        data["heading_sin"] = train_heading_sin
        data["heading_cos"] = train_heading_cos

        data["hour_sin"] = train_hour_sin
        data["hour_cos"] = train_hour_cos
        data["day_sin"] = train_day_sin
        data["day_cos"] = train_day_cos
        data["month_sin"] = train_month_sin
        data["month_cos"] = train_month_cos

        data = data.drop(
            columns=["latitude", "longitude", "cog", "heading", "portId"],
            axis=1
        )
        return data


class LastKnownLocation(Filter):
    """
    _summary_  Groups training data by vesselId, 
    and propogates all data from last known location

    Args:
    data (_type_): _description_ the data to be altered

    Returns:
        _type_:? _description_ the altered data

    """
    def __call__(self, data: DataFrame, max_shift_lenghts: int) -> DataFrame:
        
        all_test_data = DataFrame()

        shift_length = 1
        while (shift_length <= max_shift_lenghts):

            grouped_data = data.groupby("vesselId").apply(
                lambda x: x.sort_values("time")
                )
            grouped_data["time_diff"] = (
                grouped_data["time"]
                .diff(-shift_length)
                .dt.total_seconds()
                .abs()
            )
            original_time_and_id = grouped_data[
                [
                    "time",
                    "vesselId",
                    "latitude_sin",
                    "latitude_cos",
                    "longitude_sin",
                    "longitude_cos",
                ]
            ]
            shifted_data = grouped_data.shift(shift_length)
            shifted_data[
                [
                    "last_latitude_sin",
                    "last_latitude_cos",
                    "last_longitude_sin",
                    "last_longitude_cos",
                ]
            ] = shifted_data[
                [
                    "latitude_sin", "latitude_cos",
                    "longitude_sin", "longitude_cos"
                ]
            ]

            shifted_data[
                [
                    "time",
                    "vesselId",
                    "latitude_sin",
                    "latitude_cos",
                    "longitude_sin",
                    "longitude_cos",
                ]
            ] = original_time_and_id[
                [
                    "time",
                    "vesselId",
                    "latitude_sin",
                    "latitude_cos",
                    "longitude_sin",
                    "longitude_cos",
                ]
            ]

            # Drops all values with nan values
            result = shifted_data.dropna().reset_index(drop=True)

            all_test_data = pd.concat(
                [all_test_data, result],
                ignore_index=True
                )
            prev_shift_length = shift_length
            shift_length = math.floor(shift_length**(1.1))
            if shift_length == prev_shift_length:
                shift_length += 1
            
            print(f"Shift length: {shift_length}")

        # Uncomment the line below if you want to remove the "time" 
        # column after processing
        # data = data.drop("time", axis=1)

        return all_test_data


class AppendLastKnownData(Filter):
            
    def __call__(
        self,
        test_data: DataFrame,
        known_data: DataFrame
    ) -> DataFrame:
        """
        Groups training data by vesselId, and propogates all 
        data from last known location

        Args:
        data (_type_): _description_ the data to be altered

        Returns:
            _type_:? _description_ the altered data
        """
        # TODO: Interpolate rotation
        if not test_data["vesselId"].isin(known_data["vesselId"]).all():
            missing_vessels = test_data[
                ~test_data["vesselId"].isin(known_data["vesselId"])
            ]["vesselId"].unique()
            raise ValueError(
                (
                    f"The following vesselIds are missing in known_data: "
                    f"{missing_vessels}"
                )
            )
        print(
            test_data[~test_data["vesselId"].isin(known_data["vesselId"])][
                "vesselId"
            ].unique()
        )

        grouped_data = (
            known_data.sort_values("time")
            .groupby("vesselId")
            .tail(1)
            .reset_index(drop=True)
        )
        original_time = test_data[["time"]]
        test_data = test_data.drop("time", axis=1)

        result = pd.merge(test_data, grouped_data, how="left", on="vesselId")

        result["time_diff"] = (
            original_time["time"] - result["time"]
            ).dt.total_seconds()

        return result
    
