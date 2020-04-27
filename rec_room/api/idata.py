
from typing import List

from rec_room.datasets import load_data

class IData:
    """ Endpoint for retrieving Datasets 
    
    Methods
    -------
    get_dataset(fname)
        Retrieve the specified dataset
    """
    
    def get_dataset(self, fname:str) -> List[str]:
        data = load_data(fname)
        return data.to_csv(index=False).split('\n')