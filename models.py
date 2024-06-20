# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SelectField, IntegerField, SubmitField
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email
from flask_bcrypt import Bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()
class PigType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    order_items = db.relationship('OrderItem', back_populates='pig_type_ref')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', back_populates='order_ref', cascade="all, delete-orphan")
    total_price = db.Column(db.Float, nullable=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    pig_type_id = db.Column(db.Integer, db.ForeignKey('pig_type.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_ref = db.relationship('Order', back_populates='items')
    pig_type_ref = db.relationship('PigType', back_populates='order_items')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)