from flask import render_template, request, redirect, url_for
from extensions import db

from . import admin_bp

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