# seeddb.py
from app import app
from extensions import db
from models.user import User
from models.product import Product
from models.order import Order
from products_data import products as initial_products
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

        # 2. Seed Demo Customer User if not exists
        customer_email = "customer@gmail.com"
        customer = User.query.filter_by(email=customer_email).first()
        if not customer:
            customer = User(
                name="John Doe",
                email=customer_email,
                password=generate_password_hash("customer123"),
                roles="customer",
                status="active",
                profile_img="default_profile.png"
            )
            db.session.add(customer)
            print(f"[OK] Demo Customer created: {customer_email} (Password: customer123)")
        else:
            print(f"[INFO] Customer user already exists: {customer_email}")

        # 3. Seed Products if empty
        if not Product.query.first():
            for p in initial_products:
                new_p = Product(
                    id=p.get('id'),
                    name=p.get('title'),
                    price=float(p.get('price', 0)),
                    stock=50,
                    description=p.get('description', ''),
                    category=p.get('category', 'General'),
                    image=p.get('image', 'https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png')
                )
                db.session.add(new_p)
            print(f"[OK] Seeded {len(initial_products)} products.")
        else:
            print(f"[INFO] Products table already populated ({Product.query.count()} items).")

        # 4. Seed Mock Orders if empty
        if not Order.query.first():
            mock_orders = [
                Order(userId=1, productId=1, status='pending'),
                Order(userId=2, productId=3, status='confirmed'),
                Order(userId=1, productId=2, status='completed')
            ]
            for o in mock_orders:
                db.session.add(o)
            print(f"[OK] Seeded {len(mock_orders)} initial orders.")
        else:
            print(f"[INFO] Orders table already populated ({Order.query.count()} items).")

        db.session.commit()
        print("[SUCCESS] Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
