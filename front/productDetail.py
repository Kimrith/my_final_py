import json
from flask import render_template, request, redirect, url_for, make_response, abort, jsonify
from utils import get_products_list
from . import front_bp

@front_bp.get('/product_detail')
def product_detail_alias():
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
