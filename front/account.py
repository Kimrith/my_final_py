from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from extensions import db, limiter
from . import front_bp

@front_bp.route('/account', methods=['GET', 'POST'])
@limiter.exempt
def account():

    if 'user_id' not in session:
        flash('Please login to access your account.', 'warning')
        return redirect(url_for('front_bp.login'))
        
    from models.user import User
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('front_bp.login'))
        
    if request.method == 'POST':
        full_name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not full_name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('user/feane/account.html', user=user)
            
        existing_user = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_user:
            flash('This email is already taken by another account.', 'danger')
            return render_template('user/feane/account.html', user=user)
            
        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('user/feane/account.html', user=user)
            user.password = generate_password_hash(new_password)
            
        user.name = full_name
        user.email = email
        try:
            db.session.commit()
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')
            
    return render_template('user/feane/account.html', user=user)
