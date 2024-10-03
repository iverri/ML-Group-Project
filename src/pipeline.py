from feature_engineering_filter import Filter


class Pipeline:
    """
    The pipeline class is responsible for applying a series of filters to the data.
    """

    def __init__(self, filters: list[Filter]):
        self.filters = filters

    def apply_filters(self, data):
        """
        Applies all filters in the pipeline to the image
        """
        
        for filter in self.filters:
            data = filter(data)
        return data