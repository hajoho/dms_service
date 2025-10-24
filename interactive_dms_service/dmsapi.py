"""Collection of API calls"""

import logging
import requests
from flask import current_app

def call_info():
    """Function for checking API accessability"""

    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]    
    api_endpoint = f"http://{api_host}/dms/info"
    api_headers = {"authorization": api_auth}
    call_proxies = {"http": None, "https": None}

    logger.info("Calling endpoint %s", api_endpoint)
    
    try:
        response = requests.get(api_endpoint, headers=api_headers, timeout=30, proxies=call_proxies)
        logger.debug("HTTP Response Status: %s Text: %s", response.status_code, response.text)
        response.raise_for_status()
        logger.debug("Info request completed with status %s", response.status_code)        
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error calling info endpoint: %s", e)
        return {"error": str(e)}


def call_search(qry_fields, qry_folder):
    """Function for sending search querys to enaio"""
    
    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]    
    api_endpoint = f"http://{api_host}/api/dms/objects/search"
    api_headers = {
        "authorization": api_auth, 
        "content-type": "application/json"
        }
    call_proxies = {"http": None, "https": None}
    
    logger.info("Calling endpoint %s", api_endpoint)

    payload = {
        "query": {
            "statement": f"SELECT {qry_fields} FROM {qry_folder} WHERE zahl3<>1",
            "skipCount": 0,
            "maxItems": 100,
            "handleDeletedDocuments": "DELETED_DOCUMENTS_EXCLUDE"
            }
        }
    
    logger.debug("Search Query Payload: %s", payload)

    try:
        response = requests.post(api_endpoint, json=payload, headers=api_headers, timeout=30,  proxies=call_proxies)
        response.raise_for_status()
        logger.debug("Search request completed with status %s", response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error calling search endpoint: %s", e)
        return {"error": str(e)}


def call_schema():
    """Function to get the complete ObjectDefinition schema"""
    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]
    api_endpoint = f"http://{api_host}/api/dms/schema"
    api_headers = {"authorization": api_auth}
    call_proxies = {"http": None, "https": None}

    logger.info("Calling endpoint %s", api_endpoint)
    
    try:
        response = requests.get(api_endpoint, headers=api_headers, timeout=30, proxies=call_proxies)
        response.raise_for_status()
        logger.debug("Schema request completed with status %s", response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error calling schema endpoint: %s", e)
        return {"error": str(e)}
    



def call_objectschema(object_id):
    """Function to get the objectdefinition schema for a specific objectType"""
    logger = logging.getLogger(__name__)
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]
    api_endpoint = f"http://{api_host}/api/dms/schema/objecttype/{object_id}"
    api_headers = {"authorization": api_auth}
    call_proxies = {"http": None, "https": None}

    logger.info("Calling endpoint %s for object ID %s", api_endpoint, object_id)
    
    try:
        response = requests.get(api_endpoint, headers=api_headers, timeout=30, proxies=call_proxies)
        response.raise_for_status()
        logger.debug("Object schema request completed with status %s", response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error calling object schema endpoint (ID: %s): %s", object_id, e)
        return {"error": str(e)}
