
from src.feature_engineering_filter import (
    Filter,
    Feature_engineering_excample
)
from pandas import DataFrame

from src.preprocess_filter import (
    Sort_by_id
)

class Pipeline:
    """
    The pipeline class is responsible for applying a series of filters to the data. 
    """

    def __init__(self, filters: list[Filter]):
        self.filters = filters

    def apply_filters(self, df: DataFrame) -> DataFrame:
        """
        Applies all filters in the pipeline to the image
        """
        for filter in self.filters:
            df = filter(df)
        return df
    
    def assemble_pipeline(self) -> 'Pipeline':
        """
        Assembles the pipeline
        """
        filters = []
        filters.append(Sort_by_id())
        filters.append(Feature_engineering_excample())
        return Pipeline(filters)





















