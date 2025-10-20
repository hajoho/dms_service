"""Collection of used wtf_Forms"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class HelloForm(FlaskForm):
    """Minimal get name form"""
        
    name = StringField(
        'Your Name',
        validators=[
            DataRequired(message='Name is required'),
            Length(min=1, max=50, message='Name must be between 1 and 50 characters')
        ],
        render_kw={
            'placeholder': 'Enter your name',
            'class': 'form-control'
        }
    )
        
    submit = SubmitField(
        'Submit',
        render_kw={'class': 'btn btn-primary'}
    )
