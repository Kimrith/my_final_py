from admin import admin_bp
from flask import render_template, request, url_for, redirect
from extensions import db

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