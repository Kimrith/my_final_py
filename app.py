import requests
import json
import requests
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, abort, request, redirect, url_for, make_response
from product import products
from admin import users, products, orders

app = Flask(__name__)


@app.route('/')
def index():

    return render_template('user/feane/index.html')

@app.route('/menu')
def menu():
    # 1. Extract all categories, clean them up, and keep only unique values
    # We use .strip() to clean up trailing spaces in your data
    categories = sorted(list(set(p.get('category', '').strip() for p in products if p.get('category'))))

    return render_template('user/feane/menu.html',
        categories = categories,
        products = products
    )

@app.route('/about')
def about():
    return render_template('user/feane/about.html')

@app.route('/contact')
def book():
    return render_template('user/feane/contact.html')

@app.route('/account')
def account():
    return render_template('user/feane/account.html')

@app.route('/register')
def register():
    return render_template('user/feane/register.html')

@app.route('/login')
def login():
    return render_template('user/feane/login.html')

@app.route('/jinja')
def jinja():
    return  render_template('user/test_templete.html')


@app.get('/product')
def product_detail():
    product_title = request.args.get('product_title', '').strip().lower()

    product = next(
        (p for p in products
         if p.get('title', '').strip().lower() == product_title),
        None
    )
    # assert False, product_title
    if product is None:
        abort(404)

    return render_template(
        'user/feane/product_detail.html',
        product=product,
        products=products
    )


@app.route('/add_to_cart')
def add_to_cart():
    # 1. Get and sanitize product title from URL query parameters
    product_title = request.args.get('product_title', '').strip().lower()
    if not product_title:
        return redirect(url_for('menu'))

    # 2. Search for the product in mock database using title match
    product_data = next((p for p in products if p.get('title', '').strip().lower() == product_title), None)
    if not product_data:
        return redirect(url_for('menu'))

    # 3. Read current cart cookie list (fallback to empty list if missing/corrupted)
    try:
        cart_list = json.loads(request.cookies.get('cart', '[]'))
    except (json.JSONDecodeError, TypeError):
        cart_list = []

    # 4. Check if item already exists in cart by comparing unique IDs
    product_exists = False
    for item in cart_list:
        if item.get('id') == product_data.get('id'):
            item['qty'] += 1         # Increment quantity if item is found
            product_exists = True
            break

    # 5. Append as a new item row if it does not exist in cart list yet
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

    # 6. Save updated serialized JSON cart list data back to client browser cookies
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

    # Safe float and integer conversion checks to prevent template calculation parsing crashes
    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    tax = subtotal * 0.08
    total = subtotal + tax

    totals = {
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }

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

        # Filter out the deleted item
        updated_cart = [item for item in cart_list if item.get('id') != product_id]

        response = make_response(redirect(url_for('view_cart')))

        # If no items are left, delete the cookie completely from the browser
        if not updated_cart:
            response.delete_cookie('cart', path='/')
        else:
            # Otherwise, save the updated list back to the cookie
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

    # 1. Capture user information from the form
    name = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    # 2. Calculate totals
    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    tax = subtotal * 0.08
    final_total = subtotal + tax

    # 3. Format the message for Telegram
    order_summary = "🛒 *New Order Received!*\n\n"

    # Add Customer Details
    order_summary += f"*Customer Details:*\n"
    order_summary += f"👤 Name: {name}\n📧 Email: {email}\n📞 Phone: {phone}\n🏠 Address: {address}\n\n"

    order_summary += f"*Items:*\n"
    for item in cart_items:
        item_total = float(item.get('price', 0)) * int(item.get('qty', 1))
        order_summary += f"• {item.get('title')} (x{item.get('qty')}): ${item_total:.2f}\n"

    order_summary += f"\n*Subtotal:* ${subtotal:.2f}"
    order_summary += f"\n*Tax (8%):* ${tax:.2f}"
    order_summary += f"\n*Total Amount:* ${final_total:.2f}"

    # 4. Telegram API details (Ensure your token is secure in production)
    BOT_TOKEN = "8768134440:AAGyru3vfsmOVLLJI197E4MIDugcDhz6WmU"
    CHAT_ID = "-1003919937827"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # 5. Send request
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": order_summary,
            "parse_mode": "Markdown"
        })

        response = make_response(redirect(url_for('view_cart', show_success='true', total=f"{final_total:.2f}")))
        response.delete_cookie('cart', path='/')
        return response
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return "Sorry, there was an error processing your order."



# here is the code for contact form

@app.route('/admin/dashboard')
def dashboard():
    return render_template('admin/page/dashboard.html')

@app.route('/admin/users')
def user():
    return render_template('admin/page/user.html', users = users)

@app.route('/admin/products')
def product():
    return render_template('admin/page/product.html', products = products)

@app.route('/admin/orders')
def order():
    return render_template('admin/page/order.html', orders = orders)


if __name__ == '__main__':
    app.run(debug=True)