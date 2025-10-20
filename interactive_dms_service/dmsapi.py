"""Collection of API calls"""

import logging
import requests
from flask import current_app

def call_info():
    """Minimal endpoint for checking accessability"""

    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]    
    api_endpoint = "http://" + api_host + "/dms/info"
    api_headers = {"authorization": api_auth}
    call_proxies = {"http": None, "https": None}

    logger.info("Calling endpoint %s", api_endpoint)
    
    response = requests.get(api_endpoint, headers=api_headers, proxies=call_proxies)
    logger.debug("HTTP Response Status: %s Text: %s", response.status_code, response.text)
    
    return response.json()
