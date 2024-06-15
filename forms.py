# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField,PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

class OrderForm(FlaskForm):
    customer_name = StringField('Full Name', validators=[DataRequired()])
    customer_email = StringField('Email', validators=[DataRequired(), Email()])
    customer_address = StringField('Address', validators=[DataRequired()])
    customer_phone = StringField('Phone Number', validators=[DataRequired()])
    pig_type = SelectField('Pig Type', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(),