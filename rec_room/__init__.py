from os import path

__version__ = "1.0"
       
HOST = '127.0.0.1'
PORT = 1337

ROOT_URL = 'recroom/v%s'%(__version__)
ROOT_DIR = path.dirname(path.abspath(__file__))