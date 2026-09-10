from flask import render_template
from extensions import limiter
from . import front_bp

@front_bp.route('/contact')
@limiter.exempt
def book():
    return render_template('user/feane/contact.html')


