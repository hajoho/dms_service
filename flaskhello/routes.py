"""Routes of flask Web App"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for
from .forms import HelloForm
from .config import Config

# Create blueprint
main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    """Main page with form."""
    
    form = HelloForm()

    if form.validate_on_submit():
        form_result = form.name.data.strip()
        logger.debug("Given input: %s", form_result)

        return redirect(url_for('main.result', name=form_result))
    
    # Log form validation errors if any
    if form.errors:
        logger.warning("Form validation errors: %s", form.errors)

    return render_template('index.html', form=form, app_title=Config.APP_TITLE)


@main.route('/result')
def result():
    """Simple result route"""
    arg_name = request.args.get('name', 'NO NAME GIVEN')
    message = f"Hello, {arg_name}! Welcome to the demo app."
    return render_template('result.html', greeting_message=message, name=arg_name, success=True)

@main.route('/status')
def status_check():
    """Simple status endpoint."""
    logger.debug("Status requested")
    return {
        'status': 'healthy',
        'app': Config.APP_TITLE,
        'environment': Config.FLASK_ENV
    }
