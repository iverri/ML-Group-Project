from abc import ABC, abstractmethod

class Filter(ABC):
    """Filter is an abstract class that defines the interface for all filters

    Args:
        ABC (_type_): _description_ abstract class/ interface
    """
    @abstractmethod
    def __call__(self):
        """_summary_ apply the preprocessing filter to the data, so that the filter is callable. 

        Args:
            
        """
        pass
    
    