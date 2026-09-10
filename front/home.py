from flask import render_template
from extensions import limiter
from . import front_bp

@front_bp.route('/')
@limiter.exempt
def index():
    return render_template('user/feane/index.html')


