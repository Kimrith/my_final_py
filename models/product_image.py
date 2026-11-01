from extensions import db
from sqlalchemy.orm import synonym

class ProductImage(db.Model):
    __tablename__ = 'product_image'

    id = db.Column(db.Integer, primary_key=True)
    ProductId = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Aliases / Synonyms
    product_id = synonym('ProductId')
    image = synonym('name')

    def __repr__(self):
        return f"<ProductImage {self.id}: {self.name}>"
