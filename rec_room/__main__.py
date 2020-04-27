import argparse

import rec_room as rec

from rec_room import rec_api

CONFIG_CHOICES = ['debug', 'live']

def main() -> None:
    """ Main entrypoint for the application """
    parser = argparse.ArgumentParser(description='Recommender Room',
                                     prefix_chars='-')
                             
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='display additional information to the terminal')
    
    parser.add_argument('-o', '--host', required=False, default=rec.HOST,
                        help='select hostname or IP address for the web application')
                        
    parser.add_argument('-p', '--port', type=int, required=False, default=rec.PORT,
                        help='select port for the web application')
                        
    parser.add_argument('-cfg', '--configuration', dest='config', required=False,
                        choices=CONFIG_CHOICES, default='debug', 
                        help='set the appropriate configuration settings for the web application')
                        
    args = parser.parse_args()    
    rec_api.start_server(args)
    
    
if __name__ == "__main__":
    main()