
from abc import ABC, abstractmethod

class BaseRS(ABC):
    """ Base class for all Recommender Systems 
    
    All Recommender Systems integrated into the `Recommender Room`
    must inherit from the `BaseRS` class to ensure the appropriate 
    methods and properties are defined. The `Rec Room` will 
    call the methods or use the properties at runtime.
    """
    def __init__(self, args, path):
        self.args = args
        self.path = path
        
        super().__init__()

    @property 
    @abstractmethod
    def dataset(self):
        """ return the dataset and labels """
        raise NotImplementedError
        
    @property
    @abstractmethod
    def model(self):        
        """ return the trained model """
        raise NotImplementedError        
                        
    @abstractmethod
    def recommend(self, args):
        """ make a recommendation """
        raise NotImplementedError
        
    @abstractmethod
    def _train(self):
        """ train, or re-train the model """
        raise NotImplementedError
        
    @abstractmethod
    def render(self):
        """ return HTML """
        raise NotImplementedError
        
    @abstractmethod
    def visualize(self, args):
        """ return config options for chart.js """
        raise NotImplementedError
        
    

    