from filter import Filter
import numpy as np
import pandas as pd


class Sequence_training_data(Filter):
    """Sequence_training_data concatenates latitude and longtitude as a twodimensional target"""

    def __call__(self, data, time_diff_scaler):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable.

        Args:
            data (_type_): pandas data grid sorted by vesselID

        Returns:
            _type_:? pandas data grid, with concatenated latitude and longtitude as two dimensional target
        """
        sequence_length = 5
        sequences_list = []
        targets_list = []

        for vesselID, row in data.iterrows():
            sequences = row[0]

            for sequence_entry in range(sequence_length, len(sequences) - 1):
                prediction_sequences = sequences[
                    max(0, sequence_entry - sequence_length) : sequence_entry
                ]
                last_prediction_sequence_entry = prediction_sequences[-1]
                target_sequence_entry = sequences[sequence_entry + 1]

                timediff_from_last_sequence = (
                    pd.to_datetime(target_sequence_entry[0])
                    - pd.to_datetime(last_prediction_sequence_entry[0])
                ).total_seconds()
                timediff_scaled = time_diff_scaler.transform(
                    [[timediff_from_last_sequence]]
                )[0][0]

                last_prediction_sequence_entry[-1] = timediff_scaled
                prediction_sequences[-1] = last_prediction_sequence_entry

                target_sequence_entry = target_sequence_entry[
                    5:7
                ]  # the current version does not iterate over outputs, so we only need the lat and longtitude
                
                sequences_list.append(prediction_sequences)
                targets_list.append(target_sequence_entry)
                

        return np.array(sequences_list)[:,:,1:].astype('float32'), np.array(targets_list,dtype="float32")


# ,vesselId,Sequences,Target
# 0,61e9f38eb937134a3c4bfd8b,[],"[0.4700906723249091, 0.7072438410760071]"
# 1,61e9f38eb937134a3c4bfd8b,"[[Timestamp('2024-01-12 14:31:00'), 0.8544444444444446, 0.5176470588235295, 0.6125244618395302, 0.0, 0.46943123878351756, 0.7075355950869099, 0.001145925272726619]]","[0.47062155849335663, 0.707012482831543]"
# 2,61e9f38eb937134a3c4bfd8b,"[[Timestamp('2024-01-12 14:31:00'), 0.8544444444444446, 0.5176470588235295, 0.6125244618395302, 0.0, 0.46943123878351756, 0.7075355950869099, 0.001145925272726619], [Timestamp('2024-01-12 14:57:23'), 0.8522222222222223, 0.5176470588235295, 0.6105675146771037, 0.0, 0.4700906723249091, 0.7072438410760071, 0.0010164692795734025]]","[0.47112552553002784, 0.7067869302059475]"


class Feature_engineering_excample(Filter):
    """Feature_engineering_excample is a filter class that does some feature engineering"""

    def __call__(self, data):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable.

        Args:

            data (_type_): _description_ the data to be sorted

        Returns:
            _type_:? _description_ the sorted data
        """

        # TODO: implement the feature engineering
        pass


class Feature_engineering_excample2(Filter):
    """Excample of a second feature engineering filter"""

    def __call__(self, data):
        # TODO: implement a feature engineering filter here
        pass
