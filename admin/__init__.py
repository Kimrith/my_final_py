from flask import Blueprint, request, session, redirect, url_for

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder= 'templetes')

@admin_bp.before_request
def require_login():
    if request.endpoint == 'admin_bp.login':
        return None
    if 'admin_user_id' not in session or session.get('admin_role') != 'admin':
        return redirect(url_for('admin_bp.login'))

from . import dashboard
from . import user
from . import product
from . import order
from . import logout