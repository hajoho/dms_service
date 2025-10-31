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
            Length(min=1, max=100, message='Folder name must be between 1 and 100 characters')
        ],
        render_kw={
            'placeholder': 'Enter internal folder name',
            'class': 'form-control'
        }
    )
    
    field = StringField(
        'Internal field name',
        validators=[
            Length(min=1, max=100, message='Field name must be between 1 and 100 characters')
        ],
        render_kw={
            'placeholder': 'Enter internal field name',
            'class': 'form-control'
        }
    )    
    
    condition = StringField(
        'Contents for WHERE clause',
        
        render_kw={
            'placeholder': 'Enter search conditions',
            'class': 'form-control'
        }        
    )

        
    search = SubmitField(
        'Search',
        render_kw={'class': 'btn btn-primary'}
    )


class UpdateForm(FlaskForm):
    """Simple Set Field to Value Form"""
    
    field = StringField(
        'Internal field name',
        validators=[
            DataRequired(message='Provide a field name'),
            Length(min=1, max=100, message='Field name must be between 1 and 100 characters')
        ],

        render_kw={
            'placeholder': 'Enter internal field name',
            'class': 'form-control'
        }        
    )
    
    new_value = StringField(
        'The value that is written to the given field',
        render_kw={
            'placeholder': 'Enter new value',
            'class': 'form-control'
        }        
    )    
    
    start = SubmitField(
        'Start Dry Run',
        render_kw={'class': 'btn btn-primary'}
    )    