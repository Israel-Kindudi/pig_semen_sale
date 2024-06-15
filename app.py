# app.py
from flask import Flask, render_template, url_for, flash, redirect, request,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from forms import LoginForm
from flask_login import login_user, logout_user, login_required
from config import Config
from models import db, PigType, Order, User
from forms import OrderForm, RegistrationForm
from auth import auth_bp
from io import BytesIO
from weasyprint import HTML
from flask_bcrypt import Bcrypt
#from auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
#app.register_blueprint(auth_bp)
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    pig_types = PigType.query.all()
    return render_template('index.html', pig_types=pig_types)

@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    pig_types = PigType.query.all()
    form.pig_type.choices = [(pig.id, pig.name) for pig in pig_types]

    pig_type_id = request.args.get('pig_type_id', type=int)
    if pig_type_id:
        form.pig_type.data = pig_type_id

    if form.validate_on_submit():
        selected_pig = PigType.query.get(form.pig_type.data)
        total_price = form.quantity.data * selected_pig.price

        order = Order(
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            customer_address=form.customer_address.data,
            customer_phone=form.customer_phone.data,
            pig_type_id=form.pig_type.data,
            quantity=form.quantity.data,
            total_price=total_price,
        )
        db.session.add(order)
        db.session.commit()
        flash('Your order has been placed!', 'success')
        return redirect(url_for('invoice', order_id=order.id))

    return render_template('order.html', form=form)

    
@app.route('/invoice/<int:order_id>')
def invoice(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('invoice.html', order=order)
@app.route('/invoice/<int:order_id>/download')
def invoice_download(order_id):
    order = Order.query.get_or_404(order_id)
    html = render_template('invoice_pdf.html', order=order)
    pdf = HTML(string=html).write_pdf()
    response = BytesIO(pdf)
    response.seek(0)
    return send_file(response, as_attachment=True, download_name=f'invoice_{order_id}.pdf')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email a