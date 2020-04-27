from flask import (
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    session,
    flash,
    Markup
)
from flask_restful import Resource
from functools import wraps
from typing import (
    Union, 
    Tuple, 
    Dict, 
    List, 
    Callable
)


import json

from rec_room.api import (
    IData, 
    IDb,
    IRecommend
)

import rec_room as rec


SUCCESS_CODES = [200]
HEADERS = {'ContentType': 'application/json'}

def response(status:int, data:Dict=None) -> Tuple[Dict,int,Dict]:
    """
    Returns an HTTP response without HTML

    Parameters
    ----------
    status : int
        HTTP status code

    data : dictionary
        Arguments to return as part of response
        
    Returns
    -------
    tuple
        JSON data, HTTP status code, and HTTP JSON Headers
    """
    success = True if status in SUCCESS_CODES else False  
    data = {'success': success} if data is None else data
    headers = {'ContentType': 'application/json',
               'mimetype': 'application/json',
               'Connection': 'Keep-Alive',
               'Origin': '*',
               'X-Requested-With': '*',
               'Accept': '*',
               'x-auth': '*',
               'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Headers': '*'}
    
    return json.dumps(data), status, headers

def render(endpoint:str, title:str, **kwargs:Dict) -> Tuple[str,int,Dict]:
    """
    Returns an HTTP response with HTML

    Parameters
    ----------
    endpoint : str
        The endpoint being reached from the browser

    title : str
        The text to be displayed on the browser's tab
    
    kwargs : dict
        Endpoint-specific arguments
        
    Returns
    -------
    tuple
        HTML, HTTP status code, and HTTP JSON Headers
    """
    return make_response(
        render_template('%s.html'%(endpoint),
                        title='Rec Room - %s'%(title),
                        **kwargs),
         200, HEADERS)

def _df_to_dict(df:'DataFrame', cols:Union[str,List]=None, idx:int=None) -> Dict:
    """
    Converts DataFrame `df` to Dict based on input

    Parameters
    ----------
    df : DataFrame
        The DataFrame to be converted

    cols : str or List
        Column name(s) to subset `df`
    
    idx : int
        Row index to subset `df`
        
    Returns
    -------
    None
        If `df` is empty
    Dict
        Converted DataFrame
    """
    if df.empty:
        return None
    if cols is None:
        cols = df.columns
    if not isinstance(cols, list):
        cols = list(cols)    
    if idx is None:
        return df.to_records()        
    return dict(zip(cols, tuple(df[cols].values[idx])))
    
    
def login_required(f:Callable) -> Tuple:
    """
    Wraps endpoint function `f` with a login requirement

    Parameters
    ----------
    f : Callable function
        The function being called based on endpoint being reached (e.g., GET or POST)
        
    Returns
    -------
    Tuple
        HTML, HTTP status code, and HTTP JSON Headers
    """
    @wraps(f)
    def check_login(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return check_login
    
def logout() -> None:
    """ Removes session data """
    session['logged_in'] = False
    session.pop('username', None)

class ProfileAPI(Resource):
    """ Endpoint for User Accounts page
    
    Attributes
    ----------
    idb: IDb
        Interface to database methods
    users: DataFrame
        Users database
    profiles: DataFrame
        User Accounts database
    universities: DataFrame
        Universities database
    majors: DataFrame
        Student majors database
    designations: DataFrame
        Student grade-level designations database
    semesters: DataFrame
        Graduating semesters database
    interests: DataFrame
        Student interests database
    
    Methods
    -------
    get()
        Respond to an HTTP GET request
    
    post()
        Respond to an HTTP POST request
    
    """

    method_decorators = [login_required]
    
    def __init__(self) -> None:
        self.__idb = IDb()
        self.__users = self.__idb.get_users()
        self.__profiles = self.__idb.get_profiles()      
        self.__universities = self.__idb.get_universities()
        self.__majors = self.__idb.get_majors()
        self.__designations = self.__idb.get_designations()
        self.__semesters = self.__idb.get_semesters()
        self.__interests = self.__idb.get_interests()
    
        
    def get(self):
        
        print(">> ProfileAPI: received [GET] request")
        
        username = request.args.get('user', None)
        if username is None:
            return redirect(url_for('dashboard'))
        
        uid = session['user']['uid'] 
        
        if session['user']['username'] != username:
            redirect(url_for('login'))
                
        profiles = self.__profiles
        profile = _df_to_dict(profiles.loc[profiles['uid'] == uid], idx=0)
        
        if profile is None:
            return redirect(url_for('login'))
        
        return render('profile', title = 'Profile', heading = 'User Profile',
                      username = username, profile = profile, 
                      universities = self.__universities.to_dict(orient='records'),
                      majors = self.__majors.to_dict(orient='records'),
                      semesters = self.__semesters.to_dict(orient='records'),
                      interests = self.__interests.to_dict(orient='records'),
                      designations = self.__designations.to_dict(orient='records'))
                         

    def _get_user(self, args:Dict[str,str], users:'DataFrame') -> 'DataFrame':      
        """ Return the user with matching username """
        return users.loc[(users['username'] == args['username'])]   
        
    def _update_user(self, user:'DataFrame', args:Dict[str,str], users:'DataFrame') -> Dict[str,Union[str,int]]:
        """ Update the information for the user with matching `uid` """
        uid = user.uid.values[0]
        
        user = dict(uid = uid,
                    username = args.pop('username'),
                    password = args.pop('password'))
        
        success = self.__idb.update_user(user)
        if not success:
            return None
        
        profile = args
        profile.update({'uid': uid})
        profile['interests'] = [list(profile['interests'])]

        success = self.__idb.update_profile(profile)
        if not success:
            # TODO: if this fails, then undo update_user
            return None
        
        _ = user.pop('password')
        
        return user
    
        
    def post(self):
        print(">> ProfileAPI: received [POST] request")
        
        args = request.form        

        if args is None:
            return response(300)
        
        args = dict(args)        
        
        users = self.__users        
        user = self._get_user(args, users)

        if user.empty:
            flash('Error: Unable to update profile.', 'text-white')
        else:
            interests = request.form.getlist('interests') # special handling of multi-select
            args['interests'] = interests
            upd_user = self._update_user(user, args, users)
            if not upd_user:
                return 500                
            flash('Success: Profile updated.', 'text-white')

        return redirect(url_for('profile', user=session['user']['username']))             
        

class DashboardAPI(Resource):
    """ Endpoint for Dashboard page
    
    Attributes
    ----------
    idb: IDb
        Interface to database methods
    profiles: DataFrame
        User Accounts database
    recommenders: DataFrame
        Recommender systems database
    
    Methods
    -------
    get()
        Respond to an HTTP GET request
    
    post()
        Respond to an HTTP POST request
    
    """
    method_decorators = [login_required]
    def __init__(self):
        self.__idb = IDb()
        self.__profiles = self.__idb.get_profiles()
        self.__recommenders = self.__idb.get_recommenders()
    
    def get(self):
        print(">> DashboardAPI: received [GET] request")
        
        uid = session['user']['uid'] # key should always be here; forced login
        
        profiles = self.__profiles
        profile = _df_to_dict(profiles.loc[profiles['uid'] == uid], idx=0)
        
        if profile is None:
            return redirect(url_for('login'))
        
        recs = _df_to_dict(self.__recommenders)        

        return render(endpoint='dashboard', title='Home', 
                      username=session['user']['username'],
                      profile=profile, recs=recs, heading='Dashboard')

    
    def post(self):
        print(">> DashboardAPI: received [POST] request")
        

class DataAPI(Resource):
    """ Endpoint for retrieving datasets
    
    Attributes
    ----------
    idb: IData
        Interface to dataset methods
    
    Methods
    -------
    get()
        Respond to an HTTP GET request    
    
    """
    method_decorators = [login_required]
    def __init__(self):
        self.__idata = IData()        
        
    def get(self):
        print(">> DataAPI: received [GET] request")
        
        recid = request.args.get('recid', None)
        fname = request.args.get('filename', '.')
        
        if recid is None:
            return {'Error': 'Invalid recommender ID'}
        
        data = self.__idata.get_dataset(fname)
        
        if data is None:
            return {'Error': 'Invalid dataset ID'}
        
        return data


class RecommendAPI(Resource):
    """ Endpoint for the Recommender Systems
    
    Attributes
    ----------
    irec: IRecommend
        Interface to Recommender System methods
    rs: Object
        Recommender System model
    idb: IDb
        Interface to database methods
    profiles: DataFrame
        User Accounts database
    recommenders: DataFrame
        Recommender systems database
    
    Methods
    -------
    get()
        Respond to an HTTP GET request
    
    post()
        Respond to an HTTP POST request
    
    """
    method_decorators = [login_required]
    def __init__(self):   
        self.__irec = IRecommend()
        self.__rs = None
        self.__idb = IDb()        
        self.__profiles = self.__idb.get_profiles()
        self.__recommenders = self.__idb.get_recommenders()        
        
    def _get_test_data(self, rs:str) -> List[Dict]:
        """ Return test data for the OMS Courses and US Colleges Recommender Systems """
        if rs == 'oms':
            return [{'course_name': 'Artificial Intelligence for Robotics', 'course_id': 'CS-8803-001', 
                     'rating': 3.8086956521739133, 'workload': 14.68695652173913, 'difficulty': 3.408695652173913}, 
                    {'course_name': 'Advanced Operating Systems', 'course_id': 'CS-6210', 
                     'rating': 4.4423076923076925, 'workload': 17.326923076923077, 'difficulty': 4.211538461538462}, 
                    {'course_name': 'Bayesian Statistics', 'course_id': 'ISYE-6420', 
                     'rating': 3.4, 'workload': 10.533333333333333, 'difficulty': 2.6}]
        return [{'gre': 400, 'gpa': 3.15, 'rank': 2, 'name': 'Arizona State University'}, 
                {'gre': 580, 'gpa': 2.86, 'rank': 4, 'name': 'American University'}]
    
    def get(self):
        print(">> RecommendAPI: received [GET] request")
        
        recid = request.args.get('recid', None)
        if recid is None:
            return redirect(url_for('dashboard'))
        
        uid = session['user']['uid'] # key should always be here; forced login   
        
        profiles = self.__profiles
        profile = _df_to_dict(profiles.loc[profiles['uid'] == uid], idx=0)
        
        if profile is None:
            return redirect(url_for('login'))
                
        if not recid.isdigit():
            return redirect(url_for('dashboard'))
        
        recs = self.__recommenders
        rec = _df_to_dict(recs.loc[recs['uid'] == int(recid)], idx=0)
        
        if rec is None:
            return redirect(url_for('dashboard'))
        
        self.__rs = self.__irec.get_rs(rec)

        markup = Markup(self.__rs.render())
        """
        TODO: RS metadata (i.e., author, long description, etc.) should come from the RS module
              rather than the database
        rec = self.__rs.metadata
        """        
        test = False
        if test:
            test_data = self._get_test_data('oms')
            viz = self.__rs.visualize(test_data)
                
        return render(endpoint='recommend', 
                      title='Recommender', 
                      username=session['user']['username'],
                      profile=profile, 
                      rec=rec,
                      markup=markup,
                      #visualize=viz, # if test
                      heading=rec['name'])


    def post(self):
        """ TODO: use redirect('recommend?recid=recid&results=...') 
                  to avoid code redundancies betweent GET/POST methods
        """
        print(">> RecommendAPI: received [POST] request")

        recid = request.args.get('recid', None)
        if recid is None:
            return redirect(url_for('dashboard'))
        
        uid = session['user']['uid'] # key should always be here; forced login   
        
        profiles = self.__profiles
        profile = _df_to_dict(profiles.loc[profiles['uid'] == uid], idx=0)
        
        if profile is None:
            return redirect(url_for('login'))
                
        
        if not recid.isdigit():
            return redirect(url_for('dashboard'))
        
        recs = self.__recommenders
        rec = _df_to_dict(recs.loc[recs['uid'] == int(recid)], idx=0)
        
        if rec is None:
            return redirect(url_for('dashboard'))
        
        self.__rs = self.__irec.get_rs(rec)
                
        args = request.form        

        if args is None:
            return response(300)
        
        args = dict(args) 
        
        if 'multiselect' in self.__rs.requires:
            args['choices'] = request.form.getlist('multi')
            
        params = self.__irec.format_args(args, self.__rs.dtypes)
        result = self.__rs.recommend(params)
        markup = Markup(self.__rs.render())
        viz = self.__rs.visualize(result)
                
        return render(endpoint='recommend', 
                      title='Recommender', 
                      username=session['user']['username'],
                      profile=profile, 
                      rec=rec,
                      markup=markup,
                      visualize=viz,
                      heading=rec['name'])



class LoginAPI(Resource):
    """ Endpoint for the Login page
    
    Attributes
    ----------
    idb: IDb
        Interface to database methods
    users: DataFrame
        Users database
    profiles: DataFrame
        User Accounts database
    universities: DataFrame
        Universities database
    majors: DataFrame
        Student majors database
    designations: DataFrame
        Student grade-level designations database
    semesters: DataFrame
        Graduating semesters database
    interests: DataFrame
        Student interests database
    test: bool
        Flag to decide whether or not to write out to database
    
    Methods
    -------
    get()
        Respond to an HTTP GET request
    
    post()
        Respond to an HTTP POST request
    
    """
    
    def __init__(self):
        self.__idb = IDb()
        self.__users = self.__idb.get_users()
        self.__profiles = self.__idb.get_profiles()
        self.__universities = self.__idb.get_universities()
        self.__majors = self.__idb.get_majors()
        self.__designations = self.__idb.get_designations()
        self.__semesters = self.__idb.get_semesters()
        self.__interests = self.__idb.get_interests()
        self.TEST = False
        
    def get(self):
        print(">> LoginAPI: received [GET] request")        
        
        logout()
        return render('login', 'Login', heading='Welcome',
                      universities = self.__universities.to_dict(orient='records'),
                      majors = self.__majors.to_dict(orient='records'),
                      semesters = self.__semesters.to_dict(orient='records'),
                      interests = self.__interests.to_dict(orient='records'),
                      designations = self.__designations.to_dict(orient='records'))
    

    def _get_user(self, args:Dict[str,str], users:'DataFrame', action:str='login') -> 'DataFrame':
        """ Return the User matching the username for signup `action` 
            and additionally the password for login `action`
        """
        if action == 'login':
            return users.loc[(users['username'] == args['username']) & 
                             (users['password'] == args['password'])]
        elif action == 'signup':
            return users.loc[(users['username'] == args['username'])]
        
        
    def _create_user(self, args:Dict[str,str], users:'DataFrame') -> Dict[str,Union[str,int]]:
        """ Adds a new user to the Users database """
        uid = len(users) + 1  
        
        user = dict(uid = uid,
                    username = args.pop('username'),
                    password = args.pop('password'))
                
        success = self.__idb.add_user(user, test=self.TEST)
        if not success:
            return None
        
        profile = args
        profile.update({'uid': uid})

        success = self.__idb.add_profile(profile, test=self.TEST)
        if not success:
            # TODO: if this fails, then undo add_user
            return None
        
        _ = user.pop('password')
        
        return user
    
    def post(self):
        
        print(">> LoginAPI: received [POST] request")
        
        args = request.form             

        if args is None:
            return response(300)
        
        args = dict(args)
        action = args.pop('action')
        
        users = self.__users
        user = self._get_user(args, users, action)
        
        if action == 'login':                        
            if not user.empty:
                session['logged_in'] = True
                session['user'] =  _df_to_dict(user[['uid', 'username']], cols=['uid','username'], idx=0)
                return redirect(url_for('dashboard'))   
            else:
                flash('Error: Invalid login.', 'text-white')
                return redirect(url_for('login'))
                                                             
        elif action == 'signup':
            if not user.empty:
                flash('Error: Username already exists.', 'text-white')
                return redirect(url_for('login'))
            else:
                interests = request.form.getlist('interests') # special handling of multi-select
                args['interests'] = interests
                new_user = self._create_user(args, users)
                if not new_user:
                    return 500                
                session['logged_in'] = True
                session['user'] = new_user
                return redirect(url_for('dashboard'))
                
            return 500

        logout()     
        
        return 500

                

        
        


