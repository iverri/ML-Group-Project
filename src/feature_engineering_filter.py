from src.preprocess_filter import Filter


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
        
        #TODO: implement the feature engineering
        pass
    
class Feature_engineering_example2(Filter):
    """Excample of a second feature engineering filter
    """
    def __call__(self, data):
        #TODO: implement a feature engineering filter here
        pass