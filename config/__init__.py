import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'db_local.json')

def config():
    config_file = os.path.abspath(DB_PATH)
    
    with open(config_file, 'r') as f:
        config = f.read()
        f.close()

    config = json.loads(config)
    return config