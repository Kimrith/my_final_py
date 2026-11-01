import json
from flask import render_template, request, redirect, url_for, make_response, abort, jsonify
from utils import get_products_list, get_cart_from_cookie
from extensions import limiter
from . import front_bp

@front_bp.route('/api/products', methods=['GET'])
@limiter.exempt
def api_products():
    """API endpoint returning products with all images."""
    return jsonify(get_products_list())

@front_bp.get('/product')
@limiter.exempt
def product_detail():
    product_id = request.args.get('id', type=int)
    product_title = request.args.get('product_title', '').strip().lower()
    products_list = get_products_list()

    product = None
    if product_id:
        product = next((p for p in products_list if p.get('id') == product_id), None)
    if not product and product_title:
        product = next((p for p in products_list if p.get('title', '').strip().lower() == product_title), None)

    if product is None:
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Product not found'}), 404
        abort(404)

    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify(product)

    return render_template('user/feane/product_detail.html', product=product, products=products_list)

@front_bp.route('/add_to_cart')
def add_to_cart():
    product_id = request.args.get('id', type=int)
    product_title = request.args.get('product_title', '').strip().lower()
    products_list = get_products_list()

    product_data = None
    if product_id:
        product_data = next((p for p in products_list if p.get('id') == product_id), None)
    if not product_data and product_title:
        product_data = next((p for p in products_list if p.get('title', '').strip().lower() == product_title), None)

    if not product_data:
        return redirect(url_for('front_bp.menu'))

    cart_list = get_cart_from_cookie(request.cookies.get('cart'))

    product_exists = False
    for item in cart_list:
        if item.get('id') == product_data.get('id'):
            item['qty'] = int(item.get('qty', 1)) + 1
            product_exists = True
            break

    if not product_exists:
        cart_list.append({
            "id": product_data.get('id'),
            "title": product_data.get('title'),
            "price": float(product_data.get('price', 0)),
            "qty": 1,
            "image": product_data.get('image'),
            "images": product_data.get('images', [product_data.get('image')]),
            "category": product_data.get('category'),
            "description": product_data.get('description')
        })

    response = make_response(redirect(url_for('front_bp.view_cart', product_title=product_data.get('title'))))
    response.set_cookie('cart', json.dumps(cart_list), max_age=2592000, httponly=True, path='/')
    return response
