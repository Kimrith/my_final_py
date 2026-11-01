from flask import render_template, request, redirect, url_for, jsonify
from extensions import db
from models.categories import Category
from utils import handle_image_upload
from . import admin_bp
from auths import require_login

@admin_bp.route('/categories', methods=['GET'])
@require_login
def category():
    action = request.args.get('action')
    category_id = request.args.get('id', type=int)
    search = request.args.get('search', '').strip()

    edit_category = None
    if category_id:
        edit_category = Category.query.get(category_id)

    query = Category.query
    if search:
        query = query.filter(Category.name.ilike(f'%{search}%') | Category.description.ilike(f'%{search}%'))

    categories_list = query.all()

    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'image': c.image,
            'description': c.description
        } for c in categories_list])

    return render_template(
        'admin/page/category.html',
        categories=categories_list,
        action=action,
        edit_category=edit_category
    )

@admin_bp.route('/categories/create', methods=['POST'])
@require_login
def createCategory():
    try:
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not name:
            if request.is_json:
                return jsonify({'error': 'Category name is required'}), 400
            return "Error: Category name is required.", 400

        if Category.query.filter_by(name=name).first():
            if request.is_json:
                return jsonify({'error': 'Category already exists'}), 400
            return "Error: Category with this name already exists.", 400

        # Handle image upload
        uploaded_image = handle_image_upload(request.files.get('image')) if request.files else None
        if not uploaded_image and 'image' in data:
            uploaded_image = data.get('image')

        new_category = Category(name=name, description=description, image=uploaded_image)
        db.session.add(new_category)
        db.session.commit()

        if request.is_json:
            return jsonify({'message': 'Category created successfully', 'id': new_category.id}), 201
        return redirect(url_for('admin_bp.category'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        return f"Error creating category: {e}", 400

@admin_bp.route('/categories/update/<int:category_id>', methods=['POST', 'PUT'])
@require_login
def updateCategory(category_id):
    try:
        cat = Category.query.get_or_404(category_id)
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', cat.name).strip()
        description = data.get('description', cat.description).strip()

        if not name:
            if request.is_json:
                return jsonify({'error': 'Category name cannot be empty'}), 400
            return "Error: Category name cannot be empty.", 400

        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != category_id:
            if request.is_json:
                return jsonify({'error': 'Another category with this name already exists'}), 400
            return "Error: Category with this name already exists.", 400

        cat.name = name
        cat.description = description

        # Handle image upload
        uploaded_image = handle_image_upload(request.files.get('image')) if request.files else None
        if uploaded_image:
            cat.image = uploaded_image
        elif 'image' in data and data.get('image'):
            cat.image = data.get('image')

        db.session.commit()

        if request.is_json:
            return jsonify({'message': 'Category updated successfully'}), 200
        return redirect(url_for('admin_bp.category'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        return f"Error updating category: {e}", 400

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST', 'DELETE'])
@require_login
def deleteCategory(category_id):
    try:
        cat = Category.query.get_or_404(category_id)
        db.session.delete(cat)
        db.session.commit()

        if request.is_json:
            return jsonify({'message': 'Category deleted successfully'}), 200
        return redirect(url_for('admin_bp.category'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        return f"Error deleting category: {e}", 400
