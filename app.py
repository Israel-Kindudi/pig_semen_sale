# app.py
import os
from flask import Flask, render_template, url_for, flash, redirect, request,send_file,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from forms import LoginForm
from flask_login import login_user, logout_user, login_required
from config import Config
from models import db, PigType, Order, User,OrderItem
from forms import OrderForm, RegistrationForm
from auth import auth_bp
from io import BytesIO
from weasyprint import HTML
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
#from auth import auth_bp
from utils import generate_unique_order_id
from datetime import datetime
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
#app.register_blueprint(auth_bp)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route triggered")  # Debug statement
    if current_user.is_authenticated:
        print("User is already authenticated, redirecting to index")  # Debug statement
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        print("Form validated")  # Debug statement
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            print(f"Redirecting to: {next_page or 'admin_dashboard' if user.is_admin else 'index'}")  # Debug statement
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard') if user.is_admin else url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    else:
        print("Form not validated")  # Debug statement
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")  # Debug statement
    return render_template('login.html', form=form)

@app.route('/pigs')
def presentation():
    pig_types = PigType.query.all()
    return render_template('index.html', pig_types=pig_types)

@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    pig_types = PigType.query.all()
    pig_type_choices = [{'name': pig.name} for pig in pig_types]

    if form.validate_on_submit():
        order_id = generate_unique_order_id()
        order = Order(
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            customer_address=form.customer_address.data,
            customer_phone=form.customer_phone.data,
            total_price=0,
            
        )
        total_price = 0
        for item_form in form.items.entries:
            pig_type = PigType.query.filter_by(name=item_form.pig_type.data).first()
            if pig_type:
                order_item = OrderItem(
                    order_id=order_id,
                    pig_type_ref=pig_type,
                    quantity=item_form.quantity.data,
                    price=pig_type.price,
                    
                )
                order.items.append(order_item)
                total_price += pig_type.price * item_form.quantity.data
        order.total_price = total_price
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('invoice', order_id=order_item.order_id))
    return render_template('order.html', form=form, pig_types=pig_type_choices)
    
@app.route('/invoice/<int:order_id>')
def invoice(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('invoice.html', order=order)
@app.route('/invoice/<int:order_id>/download')
def invoice_download(order_id):
    order = Order.query.get_or_404(order_id)

    # Render the invoice template to HTML
    rendered_html = render_template('invoice_pdf.html', order=order)

    # Generate PDF
    pdf = HTML(string=rendered_html).write_pdf()

    # Define a filename for the PDF
    filename = f'invoice_{order.id}.pdf'

    # Define the path to save the PDF
    save_path = os.path.join(current_app.root_path, 'invoices', filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save the PDF to the specified path
    with open(save_path, 'wb') as f:
        f.write(pdf)

    # Send the file to the client
    return send_file(save_path, as_attachment=True, download_name=filename)

@app.route('/admin')
@login_required
def admin():
    orders = Order.query.all()
    return render_template('admin.html', orders=orders)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route('/')
def index():
    return render_template('presentation.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    return render_template('admin.html')

