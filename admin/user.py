import os
from flask import render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from extensions import db
from sqlalchemy import text
import models

from . import admin_bp

@admin_bp.route('/users')
def user():
    action = request.args.get('action')
    user_id = request.args.get('id', type=int)
    edit_user = None
    if user_id:
        edit_user = models.User.query.get(user_id)
    
    users_list = models.User.query.all()
    return render_template('admin/page/user.html', users=users_list, action=action, edit_user=edit_user)

@admin_bp.route('/products')
def product():
    from models.product import Product
    action = request.args.get('action')
    product_id = request.args.get('id', type=int)
    edit_product = None
    if product_id:
        edit_product = Product.query.get(product_id)
        
    products_list = Product.query.all()
    return render_template('admin/page/product.html', products=products_list, action=action, edit_product=edit_product)

@admin_bp.route('/orders')
def order():
    from models.order import Order
    action = request.args.get('action')
    order_id = request.args.get('id', type=int)
    edit_order = None
    if order_id:
        edit_order = Order.query.get(order_id)
        
    orders_list = Order.query.all()
    return render_template('admin/page/order.html', orders=orders_list, action=action, edit_order=edit_order)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/users/create', methods=['POST'])
def postUser():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        roles = request.form.get('roles', 'user')
        status = request.form.get('status', 'active')

        profile_img = 'default_profile.png'
        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                profile_img = filename

        new_user = models.User(
            name=name,
            email=email,
            password=password,
            roles=roles,
            status=status,
            profile_img=profile_img
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin_bp.user'))
    except Exception as e:
        db.session.rollback()
        # Check if the error is due to a duplicate email constraint violation
        if "UNIQUE constraint failed: user.email" in str(e):
            return "Error: This email address is already registered. Please use a different email.", 400
        return f"Error creating user: {e}", 400

@admin_bp.route('/users/update/<int:user_id>', methods=['POST'])
def edituser(user_id):
    try:
        user = models.User.query.get_or_404(user_id)
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.roles = request.form.get('roles', user.roles)
        user.status = request.form.get('status', user.status)
        password = request.form.get('password')
        if password:
            user.password = password
        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                user.profile_img = filename
        db.session.commit()
        return redirect(url_for('admin_bp.user'))
    except Exception as e:
        db.session.rollback()
        return f"Error updating user: {e}", 400

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST', 'DELETE'])
def deleteUser(user_id):
    try:
        user = models.User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_bp.user'))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting user: {e}", 400

@admin_bp.route('/products/create', methods=['POST'])
def createProduct():
    try:
        from models.product import Product
        name = request.form.get('name')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        description = request.form.get('description', '')
        category = request.form.get('category', 'General')
        image = request.form.get('image', 'https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png')

        new_product = Product(
            name=name,
            price=price,
            stock=stock,
            description=description,
            category=category,
            image=image
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error creating product: {e}", 400

@admin_bp.route('/products/update/<int:product_id>', methods=['POST'])
def updateProduct(product_id):
    try:
        from models.product import Product
        product = Product.query.get_or_404(product_id)
        product.name = request.form.get('name', product.name)
        product.price = request.form.get('price', type=float)
        product.stock = request.form.get('stock', type=int)
        product.description = request.form.get('description', product.description)
        product.category = request.form.get('category', product.category)
        product.image = request.form.get('image', product.image)
        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error updating product: {e}", 400

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def deleteProduct(product_id):
    try:
        from models.product import Product
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting product: {e}", 400

@admin_bp.route('/orders/update/<int:order_id>', methods=['POST'])
def updateOrder(order_id):
    try:
        from models.order import Order
        order = Order.query.get_or_404(order_id)
        order.status = request.form.get('status', order.status)
        db.session.commit()
        return redirect(url_for('admin_bp.order'))
    except Exception as e:
        db.session.rollback()
        return f"Error updating order: {e}", 400