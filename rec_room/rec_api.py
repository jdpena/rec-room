
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

import rec_room as rec

from rec_room.api.endpoints import (    
    DashboardAPI,
    DataAPI,
    LoginAPI,
    ProfileAPI,
    RecommendAPI
)

_CONFIGS = dict(debug='rec_room.configurations.DevelopmentConfig',
                live='rec_room.configurations.ProductionConfig')
               

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)

def url(endpoint:str) -> str:
    """ Appends root URL to each endpoint """
    return "/%s/%s"%(rec.ROOT_URL, endpoint)
    
@app.route('/')
def index() -> None:
    """ Renders the root URL """
    return "Recommender Room - Rec Room"
    
dashboard_url = url("dashboard")
data_url = url("data")
login_url = url("login")
profile_url = url("profile")
recommend_url = url("recommend")

api.add_resource(ProfileAPI, profile_url, endpoint='profile')
api.add_resource(DashboardAPI, dashboard_url, endpoint='dashboard')
api.add_resource(DataAPI, data_url, endpoint='data')
api.add_resource(LoginAPI, login_url, endpoint='login')
api.add_resource(RecommendAPI, recommend_url, endpoint='recommend')


def start_server(args:dict) -> None:
    """ Starts the Flask web server with the user args """
    # load the config object for development mode
    cfg = _CONFIGS[args.config]
    app.config.from_object(cfg)
    
    # use_evalex=False
    app.run(host=args.host, 
            port=args.port)



               
               
               
               
