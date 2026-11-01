from flask import render_template, request, redirect, url_for, jsonify
from extensions import db
from utils import handle_image_upload
from . import admin_bp
from auths import require_login

@admin_bp.route('/products')
@require_login
def product():
    from models.product import Product
    from models.categories import Category
    action = request.args.get('action')
    product_id = request.args.get('id', type=int)
    search = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()

    edit_product = None
    if product_id:
        edit_product = Product.query.get(product_id)

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    if selected_category:
        if selected_category.isdigit():
            query = query.filter(Product.CategoryId == int(selected_category))
        else:
            query = query.join(Product.category).filter(Category.name.ilike(selected_category))

    products_list = query.all()
    categories_list = Category.query.all()

    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'cost': float(p.Cost or 0.0),
            'price': float(p.Price or 0.0),
            'stock': p.Stock,
            'category_id': p.CategoryId,
            'category': p.category.name if p.category else 'General',
            'thumbnail': p.thumbnail,
            'description': p.description,
            'images': [
                (img.name if (img.name.startswith('http') or img.name.startswith('/')) else '/static/uploads/' + img.name)
                for img in p.images
            ]
        } for p in products_list])

    return render_template(
        'admin/page/product.html',
        products=products_list,
        categories=categories_list,
        action=action,
        edit_product=edit_product
    )

@admin_bp.route('/products/create', methods=['POST'])
@require_login
def createProduct():
    try:
        from models.product import Product
        from models.categories import Category
        from models.product_image import ProductImage

        name = request.form.get('name', '').strip()
        cost = request.form.get('Cost', type=float)
        if cost is None:
            cost = request.form.get('cost', type=float) or 0.00

        price = request.form.get('Price', type=float)
        if price is None:
            price = request.form.get('price', type=float) or 0.00

        stock = request.form.get('Stock', type=int)
        if stock is None:
            stock = request.form.get('stock', type=int) or 0

        description = request.form.get('description', '')

        # Resolve CategoryId
        cat_id = request.form.get('CategoryId', type=int) or request.form.get('category_id', type=int)
        if not cat_id:
            cat_name = request.form.get('category')
            if cat_name and str(cat_name).isdigit():
                cat_id = int(cat_name)
            elif cat_name:
                found_cat = Category.query.filter_by(name=cat_name.strip()).first()
                if found_cat:
                    cat_id = found_cat.id

        if not cat_id:
            first_cat = Category.query.first()
            if first_cat:
                cat_id = first_cat.id
            else:
                new_cat = Category(name="General", description="General Category")
                db.session.add(new_cat)
                db.session.flush()
                cat_id = new_cat.id

        # Thumbnail image upload
        uploaded_thumb = handle_image_upload(request.files.get('thumbnail') or request.files.get('image'))

        new_product = Product(
            name=name,
            thumbnail=uploaded_thumb,
            Cost=cost,
            Price=price,
            Stock=stock,
            CategoryId=cat_id,
            description=description
        )
        db.session.add(new_product)
        db.session.flush()

        # Handle multiple additional ProductImages from file upload
        extra_images = request.files.getlist('product_images') or request.files.getlist('images')
        for img_file in extra_images:
            saved_name = handle_image_upload(img_file)
            if saved_name:
                db.session.add(ProductImage(ProductId=new_product.id, name=saved_name))

        # Handle multiple additional image URLs entered as text
        image_urls_input = request.form.get('image_urls', '')
        if image_urls_input:
            urls = [u.strip() for u in image_urls_input.replace(',', '\n').split('\n') if u.strip()]
            for u in urls:
                db.session.add(ProductImage(ProductId=new_product.id, name=u))

        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error creating product: {e}", 400

@admin_bp.route('/products/update/<int:product_id>', methods=['POST'])
@require_login
def updateProduct(product_id):
    try:
        from models.product import Product
        from models.categories import Category
        from models.product_image import ProductImage

        product = Product.query.get_or_404(product_id)
        product.name = request.form.get('name', product.name)

        if 'Cost' in request.form or 'cost' in request.form:
            cost = request.form.get('Cost', type=float)
            if cost is None:
                cost = request.form.get('cost', type=float)
            if cost is not None:
                product.Cost = cost

        if 'Price' in request.form or 'price' in request.form:
            price = request.form.get('Price', type=float)
            if price is None:
                price = request.form.get('price', type=float)
            if price is not None:
                product.Price = price

        if 'Stock' in request.form or 'stock' in request.form:
            stock = request.form.get('Stock', type=int)
            if stock is None:
                stock = request.form.get('stock', type=int)
            if stock is not None:
                product.Stock = stock

        product.description = request.form.get('description', product.description)

        cat_id = request.form.get('CategoryId', type=int) or request.form.get('category_id', type=int)
        if not cat_id:
            cat_name = request.form.get('category')
            if cat_name and str(cat_name).isdigit():
                cat_id = int(cat_name)
            elif cat_name:
                found_cat = Category.query.filter_by(name=cat_name.strip()).first()
                if found_cat:
                    cat_id = found_cat.id

        if cat_id:
            product.CategoryId = cat_id

        uploaded_thumb = handle_image_upload(request.files.get('thumbnail') or request.files.get('image'))
        if uploaded_thumb:
            product.thumbnail = uploaded_thumb

        # Handle multiple additional ProductImages from file upload
        extra_images = request.files.getlist('product_images') or request.files.getlist('images')
        for img_file in extra_images:
            saved_name = handle_image_upload(img_file)
            if saved_name:
                db.session.add(ProductImage(ProductId=product.id, name=saved_name))

        # Handle multiple additional image URLs entered as text
        image_urls_input = request.form.get('image_urls', '')
        if image_urls_input:
            urls = [u.strip() for u in image_urls_input.replace(',', '\n').split('\n') if u.strip()]
            for u in urls:
                db.session.add(ProductImage(ProductId=product.id, name=u))

        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error updating product: {e}", 400

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@require_login
def deleteProduct(product_id):
    try:
        from models.product import Product
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('admin_bp.product'))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting product: {e}", 400

@admin_bp.route('/products/image/delete/<int:image_id>', methods=['GET', 'POST'])
@require_login
def deleteProductImage(image_id):
    try:
        from models.product_image import ProductImage
        img = ProductImage.query.get_or_404(image_id)
        prod_id = img.ProductId
        db.session.delete(img)
        db.session.commit()
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'success': True, 'message': 'Image deleted successfully'}), 200
        return redirect(url_for('admin_bp.product', action='edit', id=prod_id))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        return f"Error deleting image: {e}", 400