from flask import Flask, render_template
import admin
import front
from extensions import db, migrate, limiter, csrf, cors
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
csrf.init_app(app)
cors.init_app(app)

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
from models.categories import Category
from models.product_image import ProductImage

app.register_blueprint(admin.admin_bp, url_prefix='/admin')
app.register_blueprint(front.front_bp)

if __name__ == '__main__':
    app.run(debug=True)
