from flask import Flask, render_template


import admin
import front

from extensions import db, migrate, limiter
from config import Config
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error/429.html', error=e), 429

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

import models
from models.product import Product
from models.order import Order

with app.app_context():
    # Seed products if empty
    if not Product.query.first():
        from products_data import products as initial_products
        for p in initial_products:

            new_p = Product(
                id=p.get('id'),
                name=p.get('title'),
                price=p.get('price'),
                stock=50, # default stock
                description=p.get('description', ''),
                category=p.get('category', 'General'),
                image=p.get('image', 'https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png')
            )
            db.session.add(new_p)
        db.session.commit()
    # Seed a few dummy orders if empty
    if not Order.query.first():
        mock_orders = [
            Order(userId=1, productId=1, status='pending'),
            Order(userId=2, productId=3, status='confirmed'),
            Order(userId=3, productId=2, status='completed')
        ]
        for o in mock_orders:
            db.session.add(o)
        db.session.commit()

app.register_blueprint(admin.admin_bp, url_prefix='/admin')
app.register_blueprint(front.front_bp)

if __name__ == '__main__':
    app.run(debug=True)