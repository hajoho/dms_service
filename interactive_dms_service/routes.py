"""Routes of flask Web App"""

import logging
from flask import Blueprint, current_app, render_template, request, redirect, url_for, session
from .forms import SearchForm, UpdateForm
from .config import Config
from .dmsapi import call_info, call_search, call_schema, call_objectschema, call_dryrun, call_update

# Create blueprint
main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@main.route('/')
def index():
    """Sitemap of all defined routes"""
    routes = []
    
    for rule in current_app.url_map.iter_rules():

        # skip static endpoints
        if "static" in rule.endpoint:
            continue

        # try creating URLs - even for parameterized endpoints
        try:
            url = url_for(rule.endpoint, **{arg: f"<{arg}>" for arg in rule.arguments})
        except BuildError:
            url = None
        
        routes.append({
            "endpoint": rule.endpoint,
            "url": url
        })
    
    # sort routes - be aware of non-existing URLs
    routes.sort(key=lambda r: r["url"] or "")
     
    return render_template('index.html', sitemap_data=routes, app_title=Config.APP_TITLE) 

@main.route('/status')
def status_check():
    """Simple status endpoint."""
    logger.info("Status requested")
    return {
        'status': 'healthy',
        'app': Config.APP_TITLE,
        'environment': Config.FLASK_ENV
    }


@main.route('/info')
def info():
    """Minimal DMS Endpoint"""
    logger.info("Call Info Endpoint")
    return call_info()


@main.route('/search', methods=['GET', 'POST'])
def search():
    """Simple Search Form"""
    
    search_form = SearchForm()

    if search_form.validate_on_submit():
        input_field = search_form.field.data.strip()
        input_folder = search_form.folder.data.strip()
        input_condition = search_form.condition.data.strip()
        logger.info("Search for field %s in folder %s", input_field, input_folder)

        return redirect(url_for('main.result', field=input_field, folder=input_folder, condition=input_condition))
    
    # Log form validation errors if any
    if search_form.errors:
        logger.warning("Form validation errors: %s", search_form.errors)

    return render_template('search.html', form=search_form)


@main.route('/result')
def result():
    """Search result route"""

    arg_folder = request.args.get('folder', '')
    arg_field = request.args.get('field', '*')
    arg_condition = request.args.get('condition', '*')

    query_string = f"Show {arg_field} for {arg_folder} items with {arg_condition}"
    logger.debug("Search Query: %s", query_string)

    search_results = call_search(arg_field, arg_folder, arg_condition)
    
    # parse search results
    parsed_results = {
        'table_headers': [],
        'table_rows': [],
        'objects': []
    }
    
    objects = search_results.get('objects', [])
    
    # handle empty search results
    if not objects:        
    
        # Clear old search results from session data 
        session.pop('search_results', None)
        
        return render_template('result.html', result_query=query_string, result_headers=parsed_results['table_headers'], result_rows=parsed_results['table_rows'] )
    
    # use all properties from first object as table headers (exclude system properties)
    first_obj_properties = objects[0].get('properties', {})
    parsed_results['table_headers'] = [
        key for key in first_obj_properties.keys() 
        if not key.startswith('system:')
    ]
    
    # parse properties from each object in the search results
    for object in objects:
        properties = object.get('properties', {})
        
        # get objectId and objectTypeId to store search result for later 
        object_ids = {
            'objectId': properties.get('system:objectId', {}).get('value'),
            'objectTypeId': properties.get('system:objectTypeId', {}).get('value'),
        }
        parsed_results['objects'].append(object_ids)
        
        # Extract non-system properties for table content
        table_row = {}
        for key in parsed_results['table_headers']:
            prop_data = properties.get(key, {})
            table_row[key] = prop_data.get('value', '')
        
        parsed_results['table_rows'].append(table_row)    
    
    # Store search results in session for later use
    session['search_results'] = parsed_results['objects']
    logger.info("Stored %i result IDs in session", len(parsed_results['objects']))
            
    return render_template('result.html', result_query=query_string, result_headers=parsed_results['table_headers'], result_rows=parsed_results['table_rows'] )


@main.route('/update', methods=['GET', 'POST'])
def update():
    """Form asking for field to update"""
    
    update_form = UpdateForm()

    if update_form.validate_on_submit():
        input_field = update_form.field.data.strip()
        input_new_value = update_form.new_value.data.strip()
        logger.info("Update field %s to ", input_field, input_new_value)

        return redirect(url_for('main.dryrun', field=input_field, new_value=input_new_value))
    
    # Log form validation errors if any
    if update_form.errors:
        logger.warning("Form validation errors: %s", update_form.errors)

    if not session.get('search_results'):
        logger.warning("Update is not possible if there are no search results stored for this session.")
        return redirect(url_for('main.index'))
    
        
    no_of_affected_objects = len(session['search_results'])
    logger.info("Update may affect %i objects", no_of_affected_objects)

    return render_template('update.html', amount=no_of_affected_objects, form=update_form)


@main.route('/dryrun')
def dryrun():
    """1. getting the current values for a given field for all items in the stored search results 2. showing how the values will change in an update 3. preparing the payload data for the actual update"""

    arg_field = request.args.get('field', '')
    arg_new_value = request.args.get('new_value', '')

    update_string = f"Updating {arg_field} to {arg_new_value}"
    
    search_result_data = session['search_results']

    dryrun_data = call_dryrun(search_result_data, arg_field, arg_new_value)
    logger.info("Dryrun '%s' conducted for %i objects", update_string, len(dryrun_data['result_payloads']))

    # store prepared payloads for the actual update
    session['update_payloads'] = dryrun_data['result_payloads']

    return render_template('dryrun.html', update_info=update_string, update_dryrun=dryrun_data['result_dryrun'])

    


@main.route('/schema')
def schema():
    """ObjectDefinition Schema overview."""
    
    logger.info("Full Schema requested")
    
    schema_data = call_schema()
    
    object_types = []
    for obj in schema_data.get("objectTypes", []):
        object_types.append({
            "id": obj.get("id"),
            "localName": obj.get("localName"),
            "displayName": obj.get("displayName"),
            "detail_url": url_for('main.object_schema', objecttype_id=obj.get("id"))
        })
    
    object_types.sort(key=lambda x: (x["displayName"] or "").lower())
    logger.debug("Schema contains %d object types", len(object_types))
    
    return render_template('schema.html', result_json=object_types)
    



@main.route('/objectschema/<objecttype_id>')
def object_schema(objecttype_id):
    """ObjectDefinition for specific ObjectType."""
    
    logger.info("Object schema requested for ObjectType-ID %s", objecttype_id)
    
    object_schema_data = call_objectschema(objecttype_id)
    
    object_info = {
        "id": object_schema_data.get("id"),
        "localName": object_schema_data.get("localName"),
        "displayName": object_schema_data.get("displayName"),
        "baseId": object_schema_data.get("baseId"),
        "allowedChildren": [],
        "fields": []
    }

    for child_id in object_schema_data.get("allowedChildObjectTypeIds", []):
        object_info["allowedChildren"].append({
            "child_id": child_id,
            "child_url": url_for('main.object_schema', objecttype_id=child_id)
        })


    # TIL: Python List Comprehension: 
    #   new_list = [expression for member in iterable if conditional]
    
    # Extract and filter field information (exclude static fields)
    object_info["fields"] = [
        {
            "local_name": field_object.get("localName"),
            "display_name": field_object.get("displayName"),
            "type": field_object.get("propertyType")
        }
        for field_object in object_schema_data.get("fields", [])
        if field_object.get("propertyType") != "static"
    ]
    
    
    
    object_info["fields"].sort(key=lambda x: (x["display_name"] or "").lower())
    
    return render_template('objectschema.html', result_json=object_info)
