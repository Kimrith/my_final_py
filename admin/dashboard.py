from flask import render_template
from extensions import db
from sqlalchemy import text
from . import admin_bp

@admin_bp.route('/dashboard')
def dashboard():
    result = db.session.execute(text("SELECT COUNT(*) FROM user"))
    user_count = result.scalar()
    return render_template('admin/page/dashboard.html', user_count=user_count)

