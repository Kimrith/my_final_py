import requests
import json
from flask import Flask, render_template, abort, request, redirect, url_for, make_response, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import admin

from extensions import db, migrate
from config import Config
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

import models
from models.product import Product
from models.order import Order

with app.app_context():
    # Seed products if empty
    if not Product.query.first():
        from product import products as initial_products
        for p in initial_products:
            new_p = Product(
                id=p.get('id'),
                name=p.get('title'),
                price=p.get('price'),
                stock=50, # default stock
                description=p.get('description', ''),
                category=p.get('category', 'General'),
                image=p.get('image', 'https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png')
            )
            db.session.add(new_p)
        db.session.commit()
    # Seed a few dummy orders if empty
    if not Order.query.first():
        mock_orders = [
            Order(userId=1, productId=1, status='pending'),
            Order(userId=2, productId=3, status='confirmed'),
            Order(userId=3, productId=2, status='completed')
        ]
        for o in mock_orders:
            db.session.add(o)
        db.session.commit()

def get_products_list():
    return [{
        "id": p.id,
        "title": p.name,
        "price": p.price,
        "description": p.description,
        "category": p.category,
        "image": p.image,
        "stock": p.stock
    } for p in Product.query.all()]
app.register_blueprint(admin.admin_bp, url_prefix='/admin')
@app.route('/')
def index():
    return render_template('user/feane/index.html')

@app.route('/menu')
def menu():
    products_list = get_products_list()
    categories = sorted(list(set(p.get('category', '').strip() for p in products_list if p.get('category'))))
    return render_template('user/feane/menu.html', categories=categories, products=products_list)

@app.route('/about')
def about():
    return render_template('user/feane/about.html')

@app.route('/contact')
def book():
    return render_template('user/feane/contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not first_name or not last_name or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('user/feane/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('user/feane/register.html')
            
        from models.user import User
        if User.query.filter_by(email=email).first():
            flash('This email is already registered.', 'danger')
            return render_template('user/feane/register.html')
            
        try:
            new_user = User(
                name=f"{first_name} {last_name}",
                email=email,
                password=generate_password_hash(password),
                roles='customer',
                status='active',
                profile_img='default_profile.png'
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {e}', 'danger')
            
    return render_template('user/feane/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        from models.user import User
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.status != 'active':
                flash('Your account has been deactivated.', 'danger')
                return render_template('user/feane/login.html')
                
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.roles
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('user/feane/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash('Please login to access your account.', 'warning')
        return redirect(url_for('login'))
        
    from models.user import User
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        full_name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not full_name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('user/feane/account.html', user=user)
            
        existing_user = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_user:
            flash('This email is already taken by another account.', 'danger')
            return render_template('user/feane/account.html', user=user)
            
        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('user/feane/account.html', user=user)
            user.password = generate_password_hash(new_password)
            
        user.name = full_name
        user.email = email
        try:
            db.session.commit()
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')
            
    return render_template('user/feane/account.html', user=user)

@app.route('/jinja')
def jinja():
    return render_template('user/test_templete.html')

@app.get('/product')
def product_detail():
    product_title = request.args.get('product_title', '').strip().lower()
    products_list = get_products_list()
    product = next((p for p in products_list if p.get('title', '').strip().lower() == product_title), None)
    if product is None:
        abort(404)
    return render_template('user/feane/product_detail.html', product=product, products=products_list)

@app.route('/add_to_cart')
def add_to_cart():
    product_title = request.args.get('product_title', '').strip().lower()
    if not product_title:
        return redirect(url_for('menu'))
    product_data = next((p for p in get_products_list() if p.get('title', '').strip().lower() == product_title), None)
    if not product_data:
        return redirect(url_for('menu'))
    try:
        cart_list = json.loads(request.cookies.get('cart', '[]'))
    except (json.JSONDecodeError, TypeError):
        cart_list = []
    product_exists = False
    for item in cart_list:
        if item.get('id') == product_data.get('id'):
            item['qty'] += 1
            product_exists = True
            break
    if not product_exists:
        cart_list.append({
            "id": product_data.get('id'),
            "title": product_data.get('title'),
            "price": float(product_data.get('price', 0)),
            "qty": 1,
            "image": product_data.get('image'),
            "category": product_data.get('category'),
            "description": product_data.get('description')
        })
    response = make_response(redirect(url_for('view_cart', product_title=product_data.get('title'))))
    response.set_cookie('cart', json.dumps(cart_list), max_age=2592000, httponly=True, path='/')
    return response

@app.route('/cart')
def view_cart():
    cart_cookie = request.cookies.get('cart')
    try:
        cart_items = json.loads(cart_cookie) if cart_cookie else []
    except (json.JSONDecodeError, TypeError):
        cart_items = []
    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    tax = subtotal * 0.08
    total = subtotal + tax
    totals = {'subtotal': subtotal, 'tax': tax, 'total': total}
    return render_template('user/feane/cart.html', cart_items=cart_items, totals=totals)

@app.route('/update_cart_qty')
def update_cart_qty():
    action = request.args.get('action')
    product_id = request.args.get('product_id', type=int)
    cart_cookie = request.cookies.get('cart')
    if cart_cookie and product_id is not None:
        try:
            cart_list = json.loads(cart_cookie)
        except (json.JSONDecodeError, TypeError):
            cart_list = []
        for item in cart_list:
            if item.get('id') == product_id:
                if action == 'increase':
                    item['qty'] += 1
                elif action == 'decrease' and item['qty'] > 1:
                    item['qty'] -= 1
                break
        response = make_response(redirect(url_for('view_cart')))
        response.set_cookie('cart', json.dumps(cart_list), max_age=2592000, httponly=True, path='/')
        return response
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart')
def remove_from_cart():
    product_id = request.args.get('product_id', type=int)
    cart_cookie = request.cookies.get('cart')
    if cart_cookie and product_id is not None:
        try:
            cart_list = json.loads(cart_cookie)
        except (json.JSONDecodeError, TypeError):
            cart_list = []
        updated_cart = [item for item in cart_list if item.get('id') != product_id]
        response = make_response(redirect(url_for('view_cart')))
        if not updated_cart:
            response.delete_cookie('cart', path='/')
        else:
            response.set_cookie('cart', json.dumps(updated_cart), max_age=2592000, httponly=True, path='/')
        return response
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    cart_cookie = request.cookies.get('cart')
    if not cart_cookie:
        return redirect(url_for('view_cart'))
    try:
        cart_items = json.loads(cart_cookie)
    except (json.JSONDecodeError, TypeError):
        return redirect(url_for('view_cart'))
    name = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    tax = subtotal * 0.08
    final_total = subtotal + tax
    order_summary = "🛒 *New Order Received!*\n\n"
    order_summary += f"*Customer Details:*\n👤 Name: {name}\n📧 Email: {email}\n📞 Phone: {phone}\n🏠 Address: {address}\n\n"
    order_summary += f"*Items:*\n"
    for item in cart_items:
        item_total = float(item.get('price', 0)) * int(item.get('qty', 1))
        order_summary += f"• {item.get('title')} (x{item.get('qty')}): ${item_total:.2f}\n"
    order_summary += f"\n*Subtotal:* ${subtotal:.2f}\n*Tax (8%):* ${tax:.2f}\n*Total Amount:* ${final_total:.2f}"
    BOT_TOKEN = "8768134440:AAGyru3vfsmOVLLJI197E4MIDugcDhz6WmU"
    CHAT_ID = "-1003919937827"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": order_summary, "parse_mode": "Markdown"})
        response = make_response(redirect(url_for('view_cart', show_success='true', total=f"{final_total:.2f}")))
        response.delete_cookie('cart', path='/')
        return response
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return "Sorry, there was an error processing your order."


if __name__ == '__main__':
    app.run(debug=True)