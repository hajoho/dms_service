from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/index')
def index():
    user = {'username': 'Benno'}
    return render_template('index.html', title='Home', user=user)
