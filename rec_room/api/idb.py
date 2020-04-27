
from os.path import join
from typing import Dict

import json
import pandas as pd

import rec_room as rec
    
_DATABASE = dict(
    users = 'users.csv',
    profiles = 'profiles.csv',
    recommenders = 'recommenders.csv',
    universities = 'universities.csv',
    interests = 'interests.csv',
    semesters = 'semesters.csv',
    majors = 'majors.csv',
    designations = 'designations.csv'
)


class IDb:
    """ Interface methods to Databases 
    
    Attributes
    ----------
    db_path: str
        Full path to database directory
        
    Methods
    -------
    add_user(user, **kwargs)
        Add a user to the users database
    add_profile(profile, **kwargs)
        Add a user profile to the user profiles database    
    update_user(user, **kwargs)
        Update a user's information in the users database
    update_profile(profile, **kwargs)
        Update a user's profile in the profiles database    
    get_users(**kwargs)
        Return the users database
    get_profiles(**kwargs)
        Return the profiles database
    get_recommenders(**kwargs)
        Return the recommenders database
    get_universities(**kwargs)
        Return the universities database
    get_majors(**kwargs)
        Return the majors database
    get_designations(**kwargs)
        Return the designations database
    get_semesters(**kwargs)
        Return the semesters database
    get_interests(**kwargs)
        Return the interests database
    """
    def __init__(self, db_path:str = None):
        self.__db_path = db_path
        if self.__db_path is None:
            self.__db_path = join(rec.ROOT_DIR, 'db')

    
    ## ADD
    def _add_data(self, fname:str, data:Dict[str,str], **kwargs) -> bool:
        if kwargs.get('test', False):
            return True
        try:
            data.to_csv(join(self.__db_path, fname), index=False)
            return True
        except:
            return False        
    
    def add_user(self, user:Dict[str,str], **kwargs) -> bool:
        users = self.get_users()
        users = users.append(user, ignore_index=True)
        return self._add_data(_DATABASE['users'], users, **kwargs)

    def add_profile(self, profile:Dict[str,str], **kwargs) -> bool:
        profiles = self.get_profiles()
        profiles = profiles.append(profile, ignore_index=True)
        return self._add_data(_DATABASE['profiles'], profiles, **kwargs)
    
    
    ## UPDATE
    def _update_data(self, fname:str, uid:int, data:Dict[str,str], **kwargs) -> bool:
        if kwargs.get('test', False):
            return True
        try:            
            _data = self._get_data(fname)
            _data.loc[_data['uid'] == uid, list(data.keys())] = list(data.values())
            _data.to_csv(join(self.__db_path, fname), index=False)
            return True
        except:
            raise
            
    def update_user(self, user:Dict[str,str], **kwargs) -> bool:
        uid = user['uid']
        return self._update_data(_DATABASE['users'], uid, user, **kwargs)
    
    def update_profile(self, profile:Dict[str,str], **kwargs) -> bool:
        uid = profile['uid']
        return self._update_data(_DATABASE['profiles'], uid, profile, **kwargs)
    
                    
    ## GET
    def _get_data(self, fname, **kwargs) -> 'DataFrame':
        fp = join(self.__db_path, fname)
        return pd.read_csv(fp, index_col=False, na_filter=False)
        
    def get_users(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['users'], **kwargs)
    
    def get_profiles(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['profiles'], **kwargs)
    
    def get_recommenders(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['recommenders'], **kwargs)
    
    def get_universities(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['universities'], **kwargs)
    
    def get_majors(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['majors'], **kwargs)
    
    def get_designations(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['designations'], **kwargs)
    
    def get_semesters(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['semesters'], **kwargs)
    
    def get_interests(self, **kwargs) -> 'DataFrame':
        return self._get_data(_DATABASE['interests'], **kwargs)
    
    
    