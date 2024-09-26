from abc import ABC, abstractmethod
from pandas import DataFrame






class Filter(ABC):
    """Filter is an abstract class that defines the interface for all filters

    Args:
        ABC (_type_): _description_ abstract class/ interface
    """
    @abstractmethod
    def __call__(self, df: DataFrame):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            
        """
        return df
    
class Sort_by_id(Filter):
    """Sort_by_id is a filter class that sorts the data by id
    """
    def __call__(self, df: DataFrame):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            data (_type_): _description_ the data to be sorted
            
        Returns:
            _type_:? _description_ the sorted data
        """
        #TODO: implement the sorting by id
        return df
    
class Feature_engineering_excample(Filter):
    """_summary_ Feature_engineering_excample is a filter class that does some feature engineering

    """
    
    def __call__(self, df: DataFrame) -> DataFrame:
        #TODO: implement the feature engineering filter here
        return df






