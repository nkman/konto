import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')

def config():
    config_file = os.path.abspath(DB_PATH)
    
    with open(_file, 'r') as f:
        config = f.read()
        f.close()

    config = json.loads(config)
    return config