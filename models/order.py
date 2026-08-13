from extensions import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=True)
    productId = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), default='pending')
