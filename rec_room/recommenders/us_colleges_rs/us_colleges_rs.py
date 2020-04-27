from typing import Dict, List
from os.path import join

import joblib
import yaml

from rec_room.recommenders import BaseRS
from rec_room.datasets import load_us_colleges_dataset
from rec_room import ROOT_DIR
from rec_room.utils import Colors

# TODO: make this a variable in recommenders._base.py
RS_PATH = join(ROOT_DIR, 'recommenders') 

class USCollegesRS(BaseRS):
    """
    The US Colleges Recommender System.
    
    This RS outputs a university recommendation based on 3 criteria: gpa, gpa, and rank.
    A Nearest Neighbor model was trained to output university recommendations.
    The data used by this RS was obtained from:
        - https://www.kaggle.com/mylesoneill/world-university-rankings
        - https://www.kaggle.com/malapatiravi/graduate-school-admission-data/home

    Parameters
    ----------
    rs_args: Dict
        User specified arguments for preferences or constraints
    rs_dir: Str
        Directory to where the RS is located.
        
    Attributes
    ----------
    model: sklearn.linear_model.NearestNeighbor
        The trained model that has been loaded.
    labels: DataFrame
        The labels used by the `model`
    template: str
        The filepath to the HTML that will populate the `Parameters` 
        section in the Recommender page
    viz: str
        The filepath to the JavaScript options that will be used to parameterize
        the chart.js library in the Recommender page
    requires: Dict
        Metadata required to be captured in the Recommender page in order
        to make a recommendation
    dtypes: Dict
        Specifies the appropriate data type for the evaluation criteria used by the RS
    """
    META = dict(
        dataset = 'us_colleges.csv',
        model = 'us_colleges_model.sav',
        labels = 'us_colleges_labels.sav',
        path = 'us_colleges_rs',
        template = 'us_colleges_render.html',
        visualize = 'us_colleges_results.yaml'
    )
    
    def __init__(self, rs_args:Dict[str, str]=None, rs_dir:str=None) -> None:
        if rs_dir is None:
            rs_dir = join(RS_PATH, self.META['path'])            
            
        super(USCollegesRS, self).__init__(
            args=rs_args,
            path=rs_dir            
        )
        
        self._model = joblib.load(join(self.path, self.META['model']))
        self._labels = joblib.load(join(self.path, self.META['labels']))
        self._template = join(self.path, self.META['template'])
        self._viz = join(self.path, self.META['visualize'])
        
        self.requires = dict(
            multiselect = ['name']
        )
        self.dtypes = dict(
            rank = int,
            gpa = float,
            gre = int
        )
        
    @property
    def dataset(self) -> 'DataFrame':
        """ Return the US Colleges dataset. """
        return load_us_colleges_dataset()
    
    @property
    def model(self) -> 'sklearn.neighbors.NearestNeighbor':
        """ Return the saved model used by the Recommender System.
        
        The US COlleges RS uses a Nearest Neighbor model from the
        scikit-learn libary with the following parameters:
        
        NearestNeighbors(algorithm='auto', leaf_size=30, metric='minkowski',
                         metric_params=None, n_jobs=None, n_neighbors=161, 
                         p=2, radius=1.0)
        """
        return self._model
        
    @property
    def labels(self) -> 'DataFrame':
        """ Return the saved labels used by the Recommender System """
        return self._labels
    
    
    def recommend(self, args:Dict[str,str]=None) -> Dict[str, str]:
        """
        Make a Recommendation for US Colleges.

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
        
        inst = [metrics['gre'], metrics['gpa'], metrics['rank']]
        
        preds = self.model.kneighbors([inst], return_distance=False)[0]        
        recs = self.dataset.iloc[preds]              
        recs = recs[recs['name'].isin(choices)].reset_index(drop=True)[:top]
                
        return recs.to_dict('records')
    

    def _train(self) -> None:
        """ Train, or re-train, the US College RS. """
        df = self.dataset.copy()
        labels = df.pop('name')
        self.model.fit(df.values)

        
    def render(self) -> str:
        """ Return the HTML to be rendered.
        
        The HTML will be populated in the `Parameters` component of the Recommender page. 
        
        Returns 
        -------
        html: str
            HTML text to be rendered by the browser
        """
        html = None
                            
        with open(join(self.path, self._template), 'r') as f:
            html = f.read()
            
        assert html is not None
        
        opts = []
        opt = '<option value="{{uid}}">{{name}}</option>'
        vals = self.requires['multiselect']
        for name in sorted(self.dataset[vals].values):
            opts.append(opt.replace('{{uid}}', name[0]).replace('{{name}}', name[0]))

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
        
        labels = []
        vals = []
        raw = []
        for i, d in enumerate(data):
            labels.append(d['name'])
            vals.append(i+1)
            raw.append({
                "rank": d['rank'],
                "gpa": round(d['gpa'], 4),
                "gre": round(d['gre'], 4)
            })
        
        datasets = []               
        datasets.append({
                "label": "Recommendations",
                "data": vals[::-1],#[_ for _ in range([::-1],
                "backgroundColor": Colors.bg_colors[:len(data)],
                "borderColor": Colors.br_colors[:len(data)],
                "borderWidth": 1
            })
        
        tooltips = {                         
            "label": ''.join([
                'function(tooltipItems, data) {',
                    'var _vals = data.raw[tooltipItems.index];',
                    'var _label = ["Rank: " + Number.parseFloat(_vals.rank.toFixed(4)),',
                                   '"Avg GPA: " + Number.parseFloat(_vals.gpa.toFixed(4)),',
                                   '"Avg GRE: " + Number.parseFloat(_vals.gre.toFixed(4))];',
                            'return _label;}'])   
        }

        js['data']['raw'] = raw
        js['data']['labels'] = labels        
        js['data']['datasets'] = datasets
        js['options']['tooltips']['callbacks'] = tooltips        
        
        return js

    
    
if __name__ == "__main__":
    args = dict(
        choices = ['Georgia Institute of Technology', 
                   'Massachusetts Institute of Technology',
                   'Brandeis University'],
        metrics = {'gre': 650, 'gpa': 3.5, 'rank': 1},
        top = 4
    )
    rs = USCollegesRS(args)
    rec = rs.recommend()
    print(rec)