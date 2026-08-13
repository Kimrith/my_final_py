from extensions import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=50)
    description = db.Column(db.Text, nullable=True, default='')
    category = db.Column(db.String(128), nullable=True, default='General')
    image = db.Column(db.String(255), nullable=True, default='https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png')
