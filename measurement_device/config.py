import json

def load_config(file_path="config.json"):
    with open(file_path, 'r') as f:
        return json.load(f)

config = load_config()