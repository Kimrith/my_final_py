from flask import render_template
from extensions import limiter
from . import front_bp

@front_bp.route('/about')
@limiter.exempt
def about():
    return render_template('user/feane/about.html')


