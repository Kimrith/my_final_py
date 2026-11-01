from extensions import db
from sqlalchemy.orm import synonym
from models.product_image import ProductImage

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    Cost = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    Price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    Stock = db.Column(db.Integer, nullable=False, default=0)
    CategoryId = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.Text, nullable=True, default='')

    # Synonyms / Aliases for convenience and backward compatibility
    cost = synonym('Cost')
    price = synonym('Price')
    stock = synonym('Stock')
    category_id = synonym('CategoryId')
    image = synonym('thumbnail')

    # Relationships
    category = db.relationship('Category', backref=db.backref('products', lazy=True, cascade='all, delete-orphan'))
    images = db.relationship('ProductImage', backref=db.backref('product', lazy=True), cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"