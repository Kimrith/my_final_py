from flask import render_template, request, redirect, url_for
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from extensions import db
from models.user import User  # <-- Importing your User model
from utils import handle_image_upload
from . import admin_bp


@admin_bp.route('/users', methods=['GET'])
def user():
    action = request.args.get('action')
    user_id = request.args.get('id', type=int)
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()

    # 1. Fetch single user with SQL
    edit_user = None
    if user_id:
        result = db.session.execute(
            text("SELECT * FROM user WHERE id = :id"),
            {
                "id": user_id
            }
        )
        edit_user = result.fetchone()

    # 2. Build filtered list with dynamic SQL
    sql = "SELECT * FROM user WHERE 1=1"
    params = {}

    if search:
        sql += " AND (name LIKE :search OR email LIKE :search)"
        params["search"] = f"%{search}%"

    if role:
        sql += " AND roles = :role"
        params["role"] = role

    if status:
        sql += " AND status = :status"
        params["status"] = status

    # 3. Execute query and fetch all matching records
    users_list = db.session.execute(text(sql), params).fetchall()

    return render_template(
        'admin/page/user.html',
        users=users_list,
        action=action,
        edit_user=edit_user
    )


@admin_bp.route('/users/create', methods=['POST'])
def postUser():
    try:
        email = request.form.get('email', '').strip()

        # Check duplicate using ORM
        if User.query.filter_by(email=email).first():
            return "Error: This email is already registered.", 400

        uploaded_image = handle_image_upload(request.files.get('profile_img'))

        # Create new model instance
        new_user = User(
            name=request.form.get('name', '').strip(),
            email=email,
            password=generate_password_hash(request.form.get('password')),
            roles=request.form.get('roles', 'user'),
            status=request.form.get('status', 'active'),
            profile_img=uploaded_image or 'default_profile.png'
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin_bp.user'))

    except Exception as e:
        db.session.rollback()
        return f"Error creating user: {e}", 400


@admin_bp.route('/users/update/<int:user_id>', methods=['POST'])
def edituser(user_id):
    try:
        # Fetch user or return 404 automatically
        user = User.query.get_or_404(user_id)

        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.roles = request.form.get('roles', user.roles)
        user.status = request.form.get('status', user.status)

        new_password = request.form.get('password')
        if new_password:
            user.password = generate_password_hash(new_password)

        uploaded_image = handle_image_upload(request.files.get('profile_img'))
        if uploaded_image:
            user.profile_img = uploaded_image

        db.session.commit()
        return redirect(url_for('admin_bp.user'))

    except Exception as e:
        db.session.rollback()
        return f"Error updating user: {e}", 400


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST', 'DELETE'])
def deleteUser(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_bp.user'))

    except Exception as e:
        db.session.rollback()
        return f"Error deleting user: {e}", 400