import json
from flask import render_template, request, redirect, url_for, make_response
from extensions import limiter
from . import front_bp

@front_bp.route('/cart')
@limiter.exempt
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

@front_bp.route('/update_cart_qty')
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
        response = make_response(redirect(url_for('front_bp.view_cart')))
        response.set_cookie('cart', json.dumps(cart_list), max_age=2592000, httponly=True, path='/')
        return response
    return redirect(url_for('front_bp.view_cart'))

@front_bp.route('/remove_from_cart')
def remove_from_cart():
    product_id = request.args.get('product_id', type=int)
    cart_cookie = request.cookies.get('cart')
    if cart_cookie and product_id is not None:
        try:
            cart_list = json.loads(cart_cookie)
        except (json.JSONDecodeError, TypeError):
            cart_list = []
        updated_cart = [item for item in cart_list if item.get('id') != product_id]
        response = make_response(redirect(url_for('front_bp.view_cart')))
        if not updated_cart:
            response.delete_cookie('cart', path='/')
        else:
            response.set_cookie('cart', json.dumps(updated_cart), max_age=2592000, httponly=True, path='/')
        return response
    return redirect(url_for('front_bp.view_cart'))
