from src.preprocess_filter import Filter
from pandas import DataFrame


class Feature_engineering_example(Filter):
    """Feature_engineering_excample is a filter class that does some feature engineering
    """
    def __call__(self, data):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable.

        Args:

            data (_type_): _description_ the data to be sorted

        Returns:
            _type_:? _description_ the sorted data
        """

        # TODO: implement the feature engineering
        pass
    
class Feature_engineering_example2(Filter):
    """Excample of a second feature engineering filter
    """
    def __call__(self, data):
        #TODO: implement a feature engineering filter here
        pass
    
class Find_correct_port(Filter):
    """_summary_ portId
    This is a unique identifier for ports, mapped for convenience. 
    It's set by the captain in each vessel, so it can be wrong or 
    misleading in some cases, which will lead to incorrect mapping. 
    It's used as a proposal to identify the destination or origin 
    port of a vessel’s voyage. It is derived based on a prioritized 
    search on the “dest” column in the original AIS data by matching 
    on name or port codes. In cases where multiple port codes are listed 
    in the column, the last value is used. This rule can potentially lead 
    to some inconsistencies. The portId is a unique identifier for ports,

    Args:
        Filter (_type_): _description_
    """
    def __call__(self, df: DataFrame) -> Filter:
        # add a column to the dataframe that contains the destination port
        
        df.add_column('destination_port_id')
        df.add_column('origin_port_id')
        
        #TODO: find out what port is destination and what is origin
        
        pass
    
