import json
from flask import render_template, request, redirect, url_for, make_response, abort
from utils import get_products_list
from . import front_bp

@front_bp.get('/product')
def product_detail():
    product_title = request.args.get('product_title', '').strip().lower()
    products_list = get_products_list()
    product = next((p for p in products_list if p.get('title', '').strip().lower() == product_title), None)
    if product is None:
        abort(404)
    return render_template('user/feane/product_detail.html', product=product, products=products_list)

@front_bp.route('/add_to_cart')
def add_to_cart():
    product_title = request.args.get('product_title', '').strip().lower()
    if not product_title:
        return redirect(url_for('front_bp.menu'))
    product_data = next((p for p in get_products_list() if p.get('title', '').strip().lower() == product_title), None)
    if not product_data:
        return redirect(url_for('front_bp.menu'))
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
    response = make_response(redirect(url_for('front_bp.view_cart', product_title=product_data.get('title'))))
    response.set_cookie('cart', json.dumps(cart_list), max_age=2592000, httponly=True, path='/')
    return response
