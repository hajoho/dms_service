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
    
    response = requests.get(api_endpoint, headers=api_headers, timeout=30, proxies=call_proxies)
    logger.debug("HTTP Response Status: %s Text: %s", response.status_code, response.text)
    
    return response.json()


def call_search(qry_fields, qry_folder):
    """Endpoint for sending search querys to enaio"""
    
    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]    
    api_endpoint = "http://" + api_host + "/api/dms/objects/search"
    api_headers = {
        "authorization": api_auth, 
        "content-type": "application/json"
        }
    call_proxies = {"http": None, "https": None}
    
    logger.info("Calling endpoint %s", api_endpoint)

    payload = {
        "query": {
            "statement": "SELECT " + qry_fields + " FROM " + qry_folder + " WHERE zahl3<>1",
            "skipCount": 0,
            "maxItems": 100,
            "handleDeletedDocuments": "DELETED_DOCUMENTS_EXCLUDE"
            }
        }
    
    logger.debug("Search Query Payload: %s", payload)
    
    response = requests.post(api_endpoint, json=payload, headers=api_headers, timeout=30,  proxies=call_proxies)
    
    return response.json()
