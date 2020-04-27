from typing import Dict, List
from os.path import join

import joblib
import yaml

from rec_room.recommenders import BaseRS
from rec_room.datasets import load_oms_courses_dataset
from rec_room import ROOT_DIR
from rec_room.utils import Colors

# TODO: make this a variable in recommenders._base.py
RS_PATH = join(ROOT_DIR, 'recommenders') 

class OMSCoursesRS(BaseRS):
    """
    The OMS Courses Recommender System.
    
    This RS outputs course recommendations based on 3 criteria: rating, difficulty, and workload.
    A Logistc Regression classifier was trained to output course recommendations.
    The data used by this RS was obtained from:
        - www.omscentral.com

    Parameters
    ----------
    rs_args: Dict
        User specified arguments for preferences or constraints
    rs_dir: Str
        Directory to where the RS is located.
        
    Attributes
    ----------
    model: sklearn.linear_model.LogisticRegression
        The trained model that has been loaded.
    labels: sklearn.preprocessing.LabelEncoder
        The labels used by the `model`
    template: str
        The filepath to the HTML that will populate the `Parameters` 
        section in the Recommender page
    viz: str
        The filepath to the JavaScript options that will be used to parameterize
        the chart.js library in the Recommender page
    stats: DataFrame
        Relevant statistical data from the RS's dataset
    requires: Dict
        Metadata required to be captured in the Recommender page in order
        to make a recommendation
    dtypes: Dict
        Specifies the appropriate data type for the evaluation criteria used by the RS
    """
    META = dict(
        dataset = 'oms_courses.csv',
        model = 'oms_courses_model.sav',
        labels = 'oms_courses_labels.sav',
        path = 'oms_courses_rs',
        template = 'oms_courses_render.html',
        visualize = 'oms_courses_results.yaml'
    )
    
    def __init__(self, rs_args:Dict[str,str]=None, rs_dir:str=None) -> None:        

        if rs_dir is None:
            rs_dir = join(RS_PATH, self.META['path'])
        
        super(OMSCoursesRS, self).__init__(
            args=rs_args,
            path=rs_dir
        )
        
        self._model = joblib.load(join(self.path, self.META['model']))
        self._labels = joblib.load(join(self.path, self.META['labels']))
        self._template = join(self.path, self.META['template'])
        self._viz = join(self.path, self.META['visualize'])
        
        self.stats = self.dataset.groupby(['course_id','course_name']).mean().reset_index()

        self.requires = dict(
            multiselect = ['course_id', 'course_name']
        )
        self.dtypes = dict(
            rating = int,
            workload = int,
            difficulty = int
        )

        
    @property
    def dataset(self) -> 'DataFrame':
        """ Return the OMS Courses dataset. """
        return load_oms_courses_dataset()
    
    @property
    def model(self) -> 'sklearn.linear_model.LogisticRegression':
        """ Return the saved model used by the Recommender System.
        
        The OMS Course RS uses a logistic regression classifier from the
        scikit-learn library with the following parameters:
        
        LogisticRegression(C=1.0, class_weight=None, dual=False, 
                           fit_intercept=True, intercept_scaling=1, 
                           l1_ratio=None, max_iter=5000, multi_class='auto', 
                           n_jobs=None, penalty='l2', random_state=0, 
                           solver='saga', tol=0.0001, verbose=0, warm_start=False)
        """
        return self._model
        
    @property
    def labels(self) -> 'sklearn.preprocessing.LabelEncoder':
        """ Return the saved labels used by the Recommender System """
        return self._labels
    
    
    def recommend(self, args:Dict[str,str]=None) -> Dict[str, str]:
        """
        Make a Recommendation for OMS Courses.

        This function calls the pre-trained `self.model` and `self.labels`
        to make the best prediction, or recommendation, 
        for the provided instance arguments.

        Parameters
        ----------
        args: Dict
            User specified arguments for preferences or constraints

        Returns
        -------
        recs: Dict
            The recommendation results
        """
        if args is None:
            args = self.args
            
        assert args is not None
            
        metrics = args.get('metrics', None)
        choices = args.get('choices', [])
        top = args.get('top', len(choices))
        
        assert metrics is not None
        
        inst = [metrics['rating'], metrics['workload'], metrics['difficulty']]
        
        preds = self.model.predict_proba([inst])        
        preds = preds.argsort()[0][::-1] # sort pred indices in ascending order        

        courses = self.labels.inverse_transform(preds)
        
        recs = self.stats.set_index('course_name').loc[courses].reset_index()   # drop=True?
        recs = recs[recs['course_id'].isin(choices)].reset_index(drop=True)[:top]
        
        return recs.to_dict('records')    
        
    
    def _train(self) -> None:
        """ Train, or re-train, the OMS Courses RS. """
        df = self.dataset.copy()
        y, _ = df.pop('course_name'), df.pop('course_id')
        labels = self.labels.fit_transform(y)
        self.model.fit(df.values, labels)
        
        
    def render(self) -> str:
        """ Return the HTML to be rendered.
        
        The HTML will be populated in the `Parameters` component of the Recommender page. 
        
        Returns 
        -------
        html: str
            HTML text to be rendered by the browser
        """        
        html = None
        
        with open(self._template, 'r') as f:
            html = f.read()
        
        assert html is not None
        
        opts = []
        opt = '<option value="{{course_id}}">[{{course_id}}] {{course_name}}</option>'
        vals = self.requires['multiselect']
        for uid, name in self.dataset[vals].drop_duplicates().values:
            opts.append(opt.replace('{{course_id}}', uid).replace('{{course_name}}', name))        
            
        return html.replace('{{REPLACE}}', '<br/>'.join(opts))
    
    
    def visualize(self, data:List[Dict]) -> Dict[str,Dict]:
        """ Return the formatted options Dict for the chart.js library.
        
        Parameters
        ----------
        data: list
            The arguments specified by the user to be formatted for plotting
            
        Returns
        -------
        js: dict
            The arguments that will be used to create the chart/plot 
            on the `Results` section of the Recommender page.
        """
        js = None                
        
        with open(self._viz, 'r') as f:
            js = yaml.load(f, Loader=yaml.SafeLoader)
            
        assert js is not None
        
        labels = ["rating", "difficulty", "workload"]        
        
        datasets = []
        for i, d in enumerate(data):
            datasets.append({
                "label": d['course_id'],
                "data": [d['difficulty'], d['rating'], d['workload']],
                "backgroundColor": Colors.bg_colors[i],
                "borderColor": Colors.br_colors[i],
                "borderWidth": 1
            })
            
        tooltips = {             
            "title": ''.join([
                'function(tooltipItems, data){',
                     'var idx = Number(tooltipItems[0].index);',
                     'var _title = "Avg " + data.labels[idx].charAt(0).toUpperCase() + data.labels[idx].slice(1);',
                     'return _title;};']),
            "label": ''.join([
                'function(tooltipItems, data) {',
                    'return Number.parseFloat(tooltipItems.yLabel).toFixed(4);}'])
        }
        
        js['data']['labels'] = labels
        js['data']['datasets'] = datasets
        js['options']['tooltips']['callbacks'] = tooltips
        
        return js
        
        

if __name__ == "__main__":
    args = dict(
        choices = ['CS-6210', 'CS-6515', 'CS-6601', 'CS-7642'],
        metrics = {'rating': 5, 'workload': 20, 'difficulty': 5},
        top = 5
    )
    rs = OMSCoursesRS(args)
    rec = rs.recommend()
    print(rec)