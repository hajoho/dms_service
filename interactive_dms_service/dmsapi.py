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


def call_search(qry_field, qry_folder, qry_condition):
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
            "statement": f"SELECT {qry_field} FROM {qry_folder} WHERE {qry_condition}",
            "skipCount": 0,
            "maxItems": 10,
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


def call_dryrun(search_results, field_name, new_value):
    """
    Perform a dry run to preview changes before actual update.
    
    Fetches current values for the specified field from each object
    in the search results and prepares update payloads.
    
    Args:
        search_results (list): List of objects from search results, 
                               each containing at least 'system:objectId' and 'system:objectTypeId'
        field_name (str): Name of the field to be updated
        new_value (str): New value to be set for the field
    
    Returns:
        dict: Contains 'dryrun_items' list with before/after comparisons or errors,
              'payload_items' list ready for passing to the call_update
    """
    logger = logging.getLogger(__name__)
    
    # Input validation
    if not search_results:
        logger.warning("Dry run called with empty search results")
        return {"error": "No search results provided", "preview": [], "payloads": []}
    
    if not field_name or not isinstance(field_name, str):
        logger.error("Invalid field name provided: %s", field_name)
        return {"error": "Invalid field name", "preview": [], "payloads": []}
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]
    api_headers = {"authorization": api_auth}
    call_proxies = {"http": None, "https": None}
    
    dryrun_items = []
    payload_items = []
    
    logger.info("Starting dry run for %d objects, field: %s", len(search_results), field_name)
    
    for dms_object in search_results:
        try:
            object_id = dms_object.get("objectId")
            object_type_id = dms_object.get("objectTypeId")
            
            if not object_id:
                logger.warning("Object %s is missing objectId", str(dms_object))
                continue
            
            if not object_type_id:
                logger.warning("Object %s is missing objectTypeId", str(dms_object))
                continue
            
            # get current values for objectId  
            api_endpoint = f"http://{api_host}/api/dms/objects/{object_id}"            
            response = requests.get(
                api_endpoint, 
                headers=api_headers, 
                timeout=30, 
                proxies=call_proxies
            )
            response.raise_for_status()
            response_data = response.json()

            objects_list = response_data.get("objects", [])
            if not objects_list:
                error_msg = f"Object {object_id}: No valid object returned from DMS enpoint."
                logger.warning(error_msg)
                dryrun_items.append({
                    "object_id": object_id,
                    "object_type_id": object_type_id,
                    "status": "0",
                    "details": error_msg,
                    "field": field_name,
                    "current_value": "",
                    "new_value": ""
                })
                continue
            
            properties_item = objects_list[0].get("properties", {})
            if field_name not in properties_item:
                error_msg = f"Object {object_id}: Field '{field_name}' does not exist"
                logger.warning(error_msg)
                dryrun_items.append({
                    "object_id": object_id,
                    "object_type_id": object_type_id,
                    "status": "0",
                    "details": error_msg,
                    "field": field_name,
                    "current_value": "",
                    "new_value": ""
                })
                continue
            
            current_value = properties_item.get(field_name).get("value", "")
            
            # assemble valid dryrun item
            dryrun_items.append({
                    "object_id": object_id,
                    "object_type_id": object_type_id,
                    "status": "1",
                    "details": "Go",
                    "field": field_name,
                    "current_value": current_value,
                    "new_value": new_value
                })
            
            # Prepare update payload
            prepared_payload = {
                "objects": [{ 
                    "properties": {
                        "system:objectId": {"value": object_id},
                        "system:objectTypeId": {"value": object_type_id},
                        field_name: {"value": new_value}
                    }
                }]
            }
            payload_items.append(prepared_payload)
            
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error fetching object {object_id}: {e.response.status_code}"
            logger.error("%s - %s", error_msg, e)
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout fetching object {object_id}"
            logger.error(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error fetching object {object_id}: {str(e)}"
            logger.error(error_msg)
            
        except (KeyError, AttributeError, TypeError) as e:
            error_msg = f"Data parsing error: {str(e)}"
            logger.error(error_msg)
       
    logger.info(
        "Dry run completed: %d previews, %d payloads", len(dryrun_items), len(payload_items)
    )
    
    return {
        "result_dryrun": dryrun_items,
        "result_payloads": payload_items
    }


def call_update(update_payloads):
    """
    Execute batch update of DMS objects.
    
    Updates objects one by one using prepared payloads from dry run.
    Each update is logged individually for traceability.
    
    Args:
        update_payloads (list): List of payload dictionaries prepared by call_dryrun,
                                each containing object properties to update
    
    Returns:
        dict: Contains 'results' list with per-object outcomes,
              'summary' with success/failure counts, and any 'errors'
    """
    logger = logging.getLogger(__name__)
    
    # Input validation
    if not update_payloads:
        logger.warning("Update called with empty payloads")
        return {
            "error": "No payloads provided",
            "results": [],
            "summary": {"total": 0, "successful": 0, "failed": 0}
        }
    
    if not isinstance(update_payloads, list):
        logger.error("Invalid payload format: expected list, got %s", type(update_payloads))
        return {
            "error": "Invalid payload format",
            "results": [],
            "summary": {"total": 0, "successful": 0, "failed": 0}
        }
    
    api_host = current_app.config["API_HOST"]
    api_auth = current_app.config["API_AUTH"]
    api_endpoint = f"http://{api_host}/api/dms/objects"
    api_headers = {
        "authorization": api_auth,
        "accept": "application/json",
        "content-type": "application/json"
    }
    call_proxies = {"http": None, "https": None}
    query_params = {"minimalResponse": "true"}
    
    update_results = []
    successful_updates = 0
    failed_updates = 0
    
    logger.info("Starting batch update for %d objects", len(update_payloads))
    
    for idx, payload in enumerate(update_payloads):
        try:
            # Extract object ID for logging
            object_id = payload.get("properties", {}).get("system:objectId", {}).get("value", "unknown")
            
            # Validate payload structure
            if "properties" not in payload:
                error_msg = f"Invalid payload structure at index {idx}: missing 'properties'"
                logger.error(error_msg)
                failed_updates += 1
                update_results.append({
                    "index": idx,
                    "object_id": object_id,
                    "status": "failed",
                    "error": error_msg
                })
                continue
            
            # Wrap payload in 'objects' array as required by API
            api_payload = {"objects": [payload]}
            
            logger.info("Updating object %s (index %d)", object_id, idx)
            logger.debug("Update payload: %s", api_payload)
            
            # Execute update request
            response = requests.post(
                api_endpoint,
                json=api_payload,
                headers=api_headers,
                params=query_params,
                timeout=30,
                proxies=call_proxies
            )
            
            # Log response details
            logger.debug(
                "Object %s response: status=%d, content=%s",
                object_id, response.status_code, response.text[:200]
            )
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            successful_updates += 1
            update_results.append({
                "index": idx,
                "object_id": object_id,
                "status": "success",
                "status_code": response.status_code,
                "response": response_data
            })
            
            logger.info("Successfully updated object %s", object_id)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text[:200]}"
            logger.error("Failed to update object %s: %s", object_id, error_msg)
            failed_updates += 1
            update_results.append({
                "index": idx,
                "object_id": object_id,
                "status": "failed",
                "status_code": e.response.status_code if hasattr(e, 'response') else None,
                "error": error_msg
            })
            
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            logger.error("Timeout updating object %s", object_id)
            failed_updates += 1
            update_results.append({
                "index": idx,
                "object_id": object_id,
                "status": "failed",
                "error": error_msg
            })
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error("Request error updating object %s: %s", object_id, error_msg)
            failed_updates += 1
            update_results.append({
                "index": idx,
                "object_id": object_id,
                "status": "failed",
                "error": error_msg
            })
            
        except (ValueError, KeyError, TypeError) as e:
            error_msg = f"Data processing error: {str(e)}"
            logger.error("Error processing payload at index %d: %s", idx, error_msg)
            failed_updates += 1
            update_results.append({
                "index": idx,
                "object_id": object_id,
                "status": "failed",
                "error": error_msg
            })
    
    # Generate summary
    summary = {
        "total": len(update_payloads),
        "successful": successful_updates,
        "failed": failed_updates,
        "success_rate": f"{(successful_updates/len(update_payloads)*100):.1f}%" if update_payloads else "0%"
    }
    
    logger.info(
        "Batch update completed: %d total, %d successful, %d failed",
        summary["total"], summary["successful"], summary["failed"]
    )
    
    return {
        "results": update_results,
        "summary": summary
    }

