# utils.py
import os
import json
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the uploaded file has a permitted extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_image_upload(file_storage):
    """Helper function to validate and save uploaded profile images."""
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_storage.save(os.path.join(upload_folder, filename))
        return filename
    return None

def get_products_list():
    """Helper function to fetch all products formatted as dictionaries."""
    from models.product import Product
    products = Product.query.all()
    result = []
    for p in products:
        img_url = p.thumbnail or p.image
        if img_url:
            if not (img_url.startswith('http://') or img_url.startswith('https://') or img_url.startswith('/')):
                img_url = '/static/uploads/' + img_url
        else:
            img_url = 'https://nftcalendar.io/storage/uploads/2022/02/21/image-not-found_0221202211372462137974b6c1a.png'

        category_name = p.category.name if p.category and hasattr(p.category, 'name') else (str(p.category) if p.category else 'General')

        # Collect all images: primary thumbnail + ProductImage records
        product_images = []
        if img_url and 'image-not-found' not in img_url:
            product_images.append(img_url)

        if p.images:
            for extra in p.images:
                ext_name = extra.name
                if ext_name:
                    if not (ext_name.startswith('http://') or ext_name.startswith('https://') or ext_name.startswith('/')):
                        ext_url = '/static/uploads/' + ext_name
                    else:
                        ext_url = ext_name
                    if ext_url not in product_images:
                        product_images.append(ext_url)

        if not product_images:
            product_images.append(img_url)

        result.append({
            "id": p.id,
            "title": p.name,
            "name": p.name,
            "price": float(p.Price if p.Price is not None else (p.price or 0.0)),
            "cost": float(p.Cost if p.Cost is not None else 0.0),
            "description": p.description or '',
            "category": category_name,
            "image": img_url,
            "thumbnail": img_url,
            "images": product_images,
            "stock": p.Stock if p.Stock is not None else (p.stock or 0)
        })
    return result

def get_cart_from_cookie(cookie_val):
    """Safely parse cart cookie into a list of normalized item dictionaries."""
    if not cookie_val:
        return []
    try:
        raw = json.loads(cookie_val)
    except (json.JSONDecodeError, TypeError):
        return []

    if isinstance(raw, dict):
        raw = [raw]
    elif not isinstance(raw, list):
        return []

    cart = []
    for raw_item in raw:
        item = None
        if isinstance(raw_item, str):
            try:
                parsed = json.loads(raw_item)
                if isinstance(parsed, dict):
                    item = parsed
            except (json.JSONDecodeError, TypeError):
                continue
        elif isinstance(raw_item, dict):
            item = raw_item

        if isinstance(item, dict):
            try:
                qty = int(item.get('qty') if item.get('qty') is not None else (item.get('quantity') or 1))
            except (ValueError, TypeError):
                qty = 1
            if qty < 1:
                qty = 1

            try:
                price = float(item.get('price', 0.0) if item.get('price') is not None else 0.0)
            except (ValueError, TypeError):
                price = 0.0

            img = item.get('image') or item.get('thumbnail') or ''
            images = item.get('images')
            if not isinstance(images, list):
                images = [img] if img else []

            normalized_item = {
                'id': item.get('id'),
                'title': item.get('title') or item.get('name') or 'Product',
                'name': item.get('name') or item.get('title') or 'Product',
                'price': price,
                'qty': qty,
                'image': img,
                'thumbnail': img,
                'images': images,
                'category': item.get('category') or 'General',
                'description': item.get('description') or ''
            }
            if normalized_item['id'] is not None:
                cart.append(normalized_item)
    return cart

