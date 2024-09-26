from abc import ABC




class Filter(ABC):
    """Filter is an abstract class that defines the interface for all filters

    Args:
        ABC (_type_): _description_ abstract class/ interface
    """

    def __call__(self):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            
        """
        pass
    
class Sort_by_id(Filter):
    """Sort_by_id is a filter class that sorts the data by id
    """
    def __call__(self, data):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            data (_type_): _description_ the data to be sorted
            
        Returns:
            _type_:? _description_ the sorted data
        """
        #TODO: implement the sorting by id
        pass






