"""Routes of flask Web App"""

import logging
from flask import Blueprint, current_app, render_template, request, redirect, url_for
from .forms import SearchForm
from .config import Config
from .dmsapi import call_info, call_search

# Create blueprint
main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/search', methods=['GET', 'POST'])
def search():
    """Simple Search Form"""
    
    new_form = SearchForm()

    if new_form.validate_on_submit():
        result_field = new_form.field.data.strip()
        result_folder = new_form.folder.data.strip()
        logger.info("Search for field %s in folder %s", result_field, result_folder)

        return redirect(url_for('main.result', field=result_field, folder=result_folder))
    
    # Log form validation errors if any
    if new_form.errors:
        logger.warning("Form validation errors: %s", new_form.errors)

    return render_template('search.html', form=new_form)


@main.route('/')
def index():
    """Sitemap of all defined routes"""
    routes = []
    
    for rule in current_app.url_map.iter_rules():

        # try creating URLs - even for parameterized endpoints
        try:
            url = url_for(rule.endpoint, **{arg: f"<{arg}>" for arg in rule.arguments})
        except Exception:
            url = None
        
        routes.append({
            "endpoint": rule.endpoint,
            "url": url
        })
    
    # sort routes - be aware of non-existing URLs
    routes.sort(key=lambda r: r["url"] or "")
     
    return render_template('index.html', sitemap_data=routes, app_title=Config.APP_TITLE) 


@main.route('/result')
def result():
    """Search result route"""

    arg_folder = request.args.get('folder', '')
    arg_fields = request.args.get('field', '*')
    logger.debug("Form Values. Field %s Folder %s", arg_fields, arg_folder)

    search_results = call_search(arg_fields, arg_folder)

    query_string = f"SELECT {arg_fields} FROM {arg_folder} WHERE zahl3<>1"

    return render_template('result.html', query=query_string, result_json=search_results)

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