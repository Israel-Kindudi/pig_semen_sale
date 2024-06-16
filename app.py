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
from flask_wtf.csrf import CSRFProtect
#from auth import auth_bp

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

if __name__ == '__main__':
   # with app.app_context():
    #    db.create_all()
        # Create an admin user (run this once)
     #   if not User.query.filter_by(username='admin').first():
     #       admin_user = User(username='admin', email='admin@example.com')
     #       admin_user.set_password('adminpass')
     #       db.session.add(admin_user)
     #       db.session.commit()
    app.run(debug=True)
