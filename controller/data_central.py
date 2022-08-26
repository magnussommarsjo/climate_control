"""functions for reading data from diffrent sources"""

import httpx
import json
import logging

log = logging.getLogger(__name__)


def get_data_from_url(url: str) -> dict:
    """
    Returns a dictionary of the url data or None if the url is not valid or error occured.
    """
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
    except httpx.RequestError as e:
        log.error(f"An error occured while requesting {e.request.url!r}")
        return None


def read_data_from_smhi() -> dict:
    """
    Returns a dictionary of the data from the SMHI API.
    """
    url = "http://opendata-download-api.smhi.se/api/version/latest/parameter/1/station/744/period/latest-hour/data.json"
    return get_data_from_url(url)
