# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField,PasswordField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from models import PigType

class PigOrderForm(FlaskForm):
    pig_type_name = SelectField('Pig Type', coerce=str, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class OrderItemForm(FlaskForm):
    pig_type = StringField('Pig Type', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class OrderForm(FlaskForm):
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=80)])
    customer_email = StringField('Email', validators=[DataRequired(), Email()])
    customer_address = StringField('Address', validators=[DataRequired(), Length(min=2, max=200)])
    customer_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
    items = FieldList(FormField(OrderItemForm), min_entries=1, max_entries=10)
    submit = SubmitField('Place Order')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.populate_pig_orders()
    
    def populate_pig_orders(self):    
        pig_types = PigType.query.all()
        choices = [(pig.name, pig.name) for pig in pig_types]
        for item_form in self.items:
            item_form.pig_type.choices = choices

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    username = StringField('username',validators=[DataRequired()])

