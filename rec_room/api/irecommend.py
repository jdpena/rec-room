from typing import Callable, Union, List, Dict

from rec_room.recommenders import _get_rs

# TODO: should be in REC DB
MAPPING = {
    1 : 'oms_courses_rs',
    2 : 'us_colleges_rs'
}

class IRecommend:  
    """ Interface to the Recommender System models
    
    Attributes
    ----------
    mapping: Dict
        Maps the RS `uid` from the Recommender database with its directory name
        
    Methods
    -------
    get_rs(meta)
        Return the RS model specified
    format_args(args, dtypes)
        Format and return the RS-required arguments `args` with appropriate data types
    """    
    def __init__(self):
        self.__mapping = MAPPING
        
    def get_rs(self, meta):
        name = self.__mapping.get(meta['uid'], None)                        
        assert name is not None  
        return _get_rs(name)
    
    def format_args(self, args:Dict[str,str], dtypes:Dict[Callable,str]) -> Dict[str,Union[List,int]]:

        metrics = dict((k, dtypes[k](v)) for k,v in args.items() 
                       if k in dtypes)
        
        choices = args['choices']        
        top = int(args['top'])
        
        return dict(metrics = metrics,
                    choices = choices,
                    top = top)
        