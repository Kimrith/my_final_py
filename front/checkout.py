import json
import requests
from flask import render_template, request, redirect, url_for, make_response, session, flash
from . import front_bp

@front_bp.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login or register to complete your checkout.', 'warning')
        return redirect(url_for('front_bp.login', next=url_for('front_bp.view_cart')))
    cart_cookie = request.cookies.get('cart')
    if not cart_cookie:
        return redirect(url_for('front_bp.view_cart'))
    try:
        cart_items = json.loads(cart_cookie)
    except (json.JSONDecodeError, TypeError):
        return redirect(url_for('front_bp.view_cart'))
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
        response = make_response(redirect(url_for('front_bp.view_cart', show_success='true', total=f"{final_total:.2f}")))
        response.delete_cookie('cart', path='/')
        return response
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return "Sorry, there was an error processing your order."
