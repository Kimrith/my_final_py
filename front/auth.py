from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, limiter
from . import front_bp

@front_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("2 per minute")
def register():

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not first_name or not last_name or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('user/feane/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('user/feane/register.html')
            
        from models.user import User
        if User.query.filter_by(email=email).first():
            flash('This email is already registered.', 'danger')
            return render_template('user/feane/register.html')
            
        try:
            new_user = User(
                name=f"{first_name} {last_name}",
                email=email,
                password=generate_password_hash(password),
                roles='customer',
                status='active',
                profile_img='default_profile.png'
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please sign in.', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(url_for('front_bp.login', next=next_page))
            return redirect(url_for('front_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {e}', 'danger')
            
    return render_template('user/feane/register.html')


@front_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("2 per minute")
def login():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        from models.user import User
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.status != 'active':
                flash('Your account has been deactivated.', 'danger')
                return render_template('user/feane/login.html')
                
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.roles
            flash(f'Welcome, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('front_bp.account'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('user/feane/login.html')

@front_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('front_bp.login'))
