from flask import flash, redirect, url_for, request, render_template, session
from werkzeug.security import check_password_hash
from extensions import db
from models.user import User
from . import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password) and user.roles == 'admin':
            if user.status != 'active':
                flash('Your account has been deactivated.', 'danger')
                return render_template('admin/page/login.html')
            
            session['admin_user_id'] = user.id
            session['admin_name'] = user.name
            session['admin_role'] = user.roles
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('admin_bp.dashboard'))
        else:
            flash('Invalid email, password, or insufficient permissions.', 'danger')
            
    return render_template('admin/page/login.html')

@admin_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('admin_user_id', None)
    session.pop('admin_name', None)
    session.pop('admin_role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_bp.login'))