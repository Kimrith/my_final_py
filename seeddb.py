# seeddb.py
from app import app
from extensions import db
from models.user import User
from models.product import Product
from models.order import Order
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        print("[+] Seeding database...")

        # 1. Seed Admin Users if not exists
        admin_email = "admin@gmail.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="System Administrator",
                email=admin_email,
                password=generate_password_hash("admin123"),
                roles="admin",
                status="active",
                profile_img="default_profile.png"
            )
            db.session.add(admin)
            print(f"[OK] Admin user created: {admin_email} (Password: admin123)")
        else:
            # Ensure existing admin user has admin role
            admin.roles = "admin"
            admin.status = "active"
            print(f"[INFO] Admin user already exists: {admin_email}")

if __name__ == '__main__':
    seed_database()
