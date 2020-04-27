from typing import Dict, Union
from os.path import join, exists

import pandas as pd

import json

import rec_room as rec

DEFAULT_PATH = join(rec.ROOT_DIR, 'datasets', 'data')

def _load_csv(fp:str) -> 'DataFrame':
    """ Return the CSV from the filepath specified """
    return pd.read_csv(fp)

def _load_json(fp:str) -> Dict:
    """ Return the JSON from the filepath specified """
    with open(fp, 'r') as f:
        return json.load(f)

def load_oms_courses_dataset() -> 'DataFrame':
    """ Return the OMS Courses dataset """
    return load_data('oms_courses.csv')

def load_us_colleges_dataset():
    """ Return the US Colleges dataset """
    return load_data('us_colleges.csv')

def load_data(fname:str) -> Union[Dict,'DataFrame']:
    """ Return the dataset from the filename specified """
    fp = join(DEFAULT_PATH, fname)
    if not exists(fp):
        return None
    name, ext = fname.split('.')  
    if ext == 'json':
        return _load_json(fp)
    elif ext == 'csv':
        return _load_csv(fp)
    