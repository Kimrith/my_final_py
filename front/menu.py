from flask import render_template
from utils import get_products_list
from extensions import limiter
from . import front_bp

@front_bp.route('/menu')
@limiter.exempt
def menu():

    products_list = get_products_list()
    categories = sorted(list(set(p.get('category', '').strip() for p in products_list if p.get('category'))))
    return render_template('user/feane/menu.html', categories=categories, products=products_list)

