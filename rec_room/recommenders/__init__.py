from ._base import BaseRS
from .us_colleges_rs.us_colleges_rs import USCollegesRS
from .oms_courses_rs.oms_courses_rs import OMSCoursesRS

def _get_rs(name:str) -> 'RecommenderSystem':
    """ Return the RS specified by `name`. """
    if name == 'us_colleges_rs':
        return USCollegesRS()
    elif name == 'oms_courses_rs':
        return OMSCoursesRS()

__all__ = ['BaseRS',
           'USCollegesRS',
           'OMSCoursesRS',
]
