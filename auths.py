from functools import wraps
from flask import redirect, request, session, url_for, flash

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_user_id' not in session or session.get('admin_role') != 'admin':
            flash('You must be logged in as admin to access this page.', 'danger')
            return redirect(url_for('admin_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged_in():
    if 'admin_user_id' in session and session.get('admin_role') == 'admin':
        return redirect(url_for('admin_bp.dashboard'))
    return None