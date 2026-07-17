function openAddProductModal() {
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.querySelector('#product-modal h3').innerText = 'Add New Product';
    document.getElementById('product-modal').classList.remove('hidden');
}

function editProduct(product) {
    document.getElementById('product-modal').classList.remove('hidden');
    document.querySelector('#product-modal h3').innerText = 'Edit Product: ' + product.name;

    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productStock').value = product.stock;
}