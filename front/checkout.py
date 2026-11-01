import json
import requests
import io
import base64
import time
import random
import qrcode
from flask import render_template, request, redirect, url_for, make_response, session, flash, jsonify
from bakong_khqr import KHQR
from config import Config
from utils import get_cart_from_cookie
from extensions import db, csrf
from models.order import Order
from . import front_bp

# Server-side dictionary to guarantee payment metadata is preserved
PENDING_PAYMENTS = {}

def send_order_telegram(order_summary):
    """Deliver order notification to Telegram with HTML parse mode and fallback."""
    BOT_TOKEN = "9054430246:AAHouqNuBsKZKW5MAwZC6pA3-Wevp8S9QmM"
    CHAT_ID = "-1004346289432"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": order_summary,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=payload, timeout=8)
        if not res.ok:
            # Fallback to plain text if HTML tags cause any issue
            payload.pop("parse_mode", None)
            requests.post(url, data=payload, timeout=8)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def save_order_records(user_id, cart_items, status='confirmed'):
    """Save order items into database."""
    try:
        for item in cart_items:
            order_rec = Order(
                userId=user_id,
                productId=item.get('id'),
                status=status
            )
            db.session.add(order_rec)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving order to DB: {e}")

def get_payment_info(md5):
    """Retrieve payment information from server memory or session."""
    info = PENDING_PAYMENTS.get(md5)
    if not info and 'pending_payment' in session and session['pending_payment'].get('md5') == md5:
        info = session['pending_payment']
    return info

def finalize_order(payment_info, user_id=None):
    """Finalize order, record in DB, and push to Telegram."""
    if not payment_info:
        return False
    if payment_info.get('completed'):
        return True

    cart_items = payment_info.get('items', [])
    customer = payment_info.get('customer', {})
    amount = float(payment_info.get('amount', 0.0))
    bill_num = payment_info.get('bill_number', 'N/A')
    uid = user_id or payment_info.get('user_id')

    # 1. Record orders in database
    save_order_records(uid, cart_items, status='confirmed')

    # 2. Push to Telegram (same structure as Cash on Delivery)
    order_summary = "🛒 <b>New Order Received!</b>\n\n"
    order_summary += "💳 <b>Payment Method:</b> 🔴 Paid via Bakong KHQR\n"
    order_summary += f"🧾 <b>Bill Number:</b> {bill_num}\n\n"
    order_summary += f"<b>Customer Details:</b>\n👤 Name: {customer.get('name')}\n📧 Email: {customer.get('email')}\n📞 Phone: {customer.get('phone')}\n🏠 Address: {customer.get('address')}\n\n"
    order_summary += "<b>Items:</b>\n"
    for item in cart_items:
        item_total = float(item.get('price', 0)) * int(item.get('qty', 1))
        order_summary += f"• {item.get('title')} (x{item.get('qty')}): ${item_total:.2f}\n"
    order_summary += f"\n<b>Subtotal:</b> ${payment_info.get('subtotal', 0):.2f}\n<b>Tax (8%):</b> ${payment_info.get('tax', 0):.2f}\n<b>Total Amount:</b> ${amount:.2f}"

    send_order_telegram(order_summary)

    # 3. Mark completed so it never double-sends
    payment_info['completed'] = True
    return True

@front_bp.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login or register to complete your checkout.', 'warning')
        return redirect(url_for('front_bp.login', next=url_for('front_bp.view_cart')))

    cart_items = get_cart_from_cookie(request.cookies.get('cart'))
    if not cart_items:
        return redirect(url_for('front_bp.view_cart'))

    name = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    payment_method = request.form.get('payment_method', 'bakong')

    subtotal = sum(float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart_items)
    tax = subtotal * 0.08
    final_total = subtotal + tax

    # 1. Cash on Delivery (COD)
    if payment_method == 'cod':
        save_order_records(session.get('user_id'), cart_items, status='pending')

        order_summary = "🛒 <b>New Order Received!</b>\n\n"
        order_summary += "💳 <b>Payment Method:</b> 💵 Cash on Delivery (COD)\n\n"
        order_summary += f"<b>Customer Details:</b>\n👤 Name: {name}\n📧 Email: {email}\n📞 Phone: {phone}\n🏠 Address: {address}\n\n"
        order_summary += "<b>Items:</b>\n"
        for item in cart_items:
            item_total = float(item.get('price', 0)) * int(item.get('qty', 1))
            order_summary += f"• {item.get('title')} (x{item.get('qty')}): ${item_total:.2f}\n"
        order_summary += f"\n<b>Subtotal:</b> ${subtotal:.2f}\n<b>Tax (8%):</b> ${tax:.2f}\n<b>Total Amount:</b> ${final_total:.2f}"

        send_order_telegram(order_summary)

        response = make_response(redirect(url_for('front_bp.view_cart', show_success='true', total=f"{final_total:.2f}")))
        response.delete_cookie('cart', path='/')
        return response

    # 2. Bakong KHQR Payment
    bill_number = f"INV{int(time.time())}{random.randint(100, 999)}"
    try:
        k = KHQR(bakong_token=Config.BAKONG_TOKEN)
        qr_result = k.create_qr(
            amount=round(final_total, 2),
            account_id=Config.BAKONG_ID,
            merchant_name=Config.BAKONG_MERCHANT_NAME,
            merchant_city=Config.BAKONG_MERCHANT_CITY,
            currency="USD",
            bill_number=bill_number,
            return_dict=True
        )
        qr_string = qr_result.get('data', {}).get('qr')
        md5_hash = qr_result.get('data', {}).get('md5')
    except Exception as e:
        print(f"Error generating KHQR: {e}")
        flash('Failed to generate Bakong KHQR. Please try again or select Cash on Delivery.', 'danger')
        return redirect(url_for('front_bp.view_cart'))

    if not qr_string or not md5_hash:
        flash('Unable to create Bakong QR code. Please try again.', 'warning')
        return redirect(url_for('front_bp.view_cart'))

    # Store lean metadata (no heavy Base64 image in cookie)
    minimal_items = []
    for item in cart_items:
        minimal_items.append({
            'id': item.get('id'),
            'title': item.get('title'),
            'price': float(item.get('price', 0)),
            'qty': int(item.get('qty', 1))
        })

    payment_record = {
        'md5': md5_hash,
        'bill_number': bill_number,
        'qr_string': qr_string,
        'amount': final_total,
        'subtotal': subtotal,
        'tax': tax,
        'merchant_name': Config.BAKONG_MERCHANT_NAME,
        'merchant_city': Config.BAKONG_MERCHANT_CITY,
        'user_id': session.get('user_id'),
        'customer': {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address
        },
        'items': minimal_items,
        'completed': False
    }

    # Store in memory dict and session
    PENDING_PAYMENTS[md5_hash] = payment_record
    session['pending_payment'] = payment_record

    return redirect(url_for('front_bp.bakong_payment', md5=md5_hash))

@front_bp.route('/payment/bakong/<md5>', methods=['GET'])
def bakong_payment(md5):
    if 'user_id' not in session:
        return redirect(url_for('front_bp.login'))

    payment_info = get_payment_info(md5)
    if not payment_info:
        flash('Payment session not found or expired.', 'warning')
        return redirect(url_for('front_bp.view_cart'))

    # Generate QR Image dynamically on demand
    qr_img = qrcode.make(payment_info['qr_string'])
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    qr_data_url = f"data:image/png;base64,{qr_base64}"
    payment_info['qr_image'] = qr_data_url

    return render_template('user/feane/bakong_payment.html', payment=payment_info)

@front_bp.route('/api/payment/check/<md5>', methods=['GET'])
@csrf.exempt
def check_payment_status(md5):
    payment_info = get_payment_info(md5)
    status = 'UNPAID'
    try:
        k = KHQR(bakong_token=Config.BAKONG_TOKEN)
        status_res = k.check_payment(md5)
        status = status_res[0] if isinstance(status_res, tuple) else status_res
    except Exception as e:
        status = 'UNPAID'

    # AS SOON AS STATUS IS PAID: Immediately finalize order and push to Telegram!
    if status == 'PAID' and payment_info:
        finalize_order(payment_info, session.get('user_id') or payment_info.get('user_id'))

    return jsonify({'status': status})

@front_bp.route('/payment/complete/<md5>', methods=['GET', 'POST'])
@csrf.exempt
def complete_bakong_payment(md5):
    payment_info = get_payment_info(md5)
    if not payment_info:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'success': False, 'message': 'Payment session expired'}), 400
        return redirect(url_for('front_bp.view_cart'))

    # Verify payment status with Bakong API if not already confirmed
    status = 'PAID' if payment_info.get('completed') else 'UNPAID'
    if status != 'PAID':
        try:
            k = KHQR(bakong_token=Config.BAKONG_TOKEN)
            status_res = k.check_payment(md5)
            status = status_res[0] if isinstance(status_res, tuple) else status_res
        except Exception as e:
            print(f"Error checking payment: {e}")

    # Allow completion if confirmed paid by Bakong, or explicit user confirmation
    is_confirmed = (status == 'PAID') or (request.args.get('confirm') == 'true') or (request.form.get('confirm') == 'true') or payment_info.get('completed')

    if is_confirmed:
        finalize_order(payment_info, session.get('user_id') or payment_info.get('user_id'))
        amount = payment_info.get('amount', 0.0)

        # Clear session
        session.pop('pending_payment', None)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            response = make_response(jsonify({'success': True, 'amount': amount}))
            response.delete_cookie('cart', path='/')
            return response

        response = make_response(redirect(url_for('front_bp.view_cart', show_success='true', total=f"{amount:.2f}")))
        response.delete_cookie('cart', path='/')
        return response

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': False, 'status': status}), 400

    flash('Payment has not been detected yet. Please ensure you scanned and confirmed the transfer in your banking app, then check again.', 'warning')
    return redirect(url_for('front_bp.bakong_payment', md5=md5))
