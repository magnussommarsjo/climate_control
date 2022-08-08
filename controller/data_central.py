"""functions for reading data from diffrent sources"""

import requests
import json

def get_data_from_url(url: str) -> dict:
    """
    Returns a dictionary of the url data or None if the url is not valid.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

def read_data_from_smhi() -> dict:
    """
    Returns a dictionary of the data from the SMHI API.
    """
    url = "http://opendata-download-api.smhi.se/api/version/latest/parameter/1/station/744/period/latest-hour/data.json"
    return get_data_from_url(url)