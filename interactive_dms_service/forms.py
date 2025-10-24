"""Collection of used wtf_Forms"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
    """Simple Search Query Form"""
        
    folder = StringField(
        'Internal Folder name',
        validators=[
            DataRequired(message='Provide a folder name'),
            Length(min=1, max=100, message='Folder name must be between 1 and 50 characters')
        ],
        render_kw={
            'placeholder': 'Enter internal folder name',
            'class': 'form-control'
        }
    )
    
    field = StringField(
        'Internal field name',
        validators=[
            Length(min=1, max=100, message='Field name must be between 1 and 50 characters')
        ],
        render_kw={
            'placeholder': 'Enter internal field name',
            'class': 'form-control'
        }
    )    
        
    submit = SubmitField(
        'Submit',
        render_kw={'class': 'btn btn-primary'}
    )
