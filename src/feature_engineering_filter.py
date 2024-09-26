from src.preprocess_filter import Filter
from pandas import DataFrame


class Feature_engineering_excample(Filter):
    """Feature_engineering_excample is a filter class that does some feature engineering
    """
    def __call__(self, df: DataFrame) -> DataFrame:
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            data (_type_): _description_ the data to be sorted
            
        Returns:
            _type_:? _description_ the sorted data
        """
        
        #TODO: implement the feature engineering
        return df
    
class Feature_engineering_excample2(Filter):
    """Excample of a second feature engineering filter
    """
    def __call__(self, df: DataFrame) -> DataFrame:
        #TODO: implement a feature engineering filter here
        return df