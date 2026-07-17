// Open modal for adding
function openAddModal() {
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.querySelector('#user-modal h3').innerText = 'Add New User';
    document.getElementById('user-modal').classList.remove('hidden');
}

// Open modal for editing
function editUser(user) {
    document.getElementById('user-modal').classList.remove('hidden');
    document.querySelector('#user-modal h3').innerText = 'Edit User: ' + user.name;

    // Fill all fields
    document.getElementById('userId').value = user.id;
    document.getElementById('userName').value = user.name;
    document.getElementById('userEmail').value = user.email;
    document.getElementById('userRole').value = user.role;
    // Logic to show 'Active' or 'Inactive' based on boolean
    document.getElementById('userStatus').value = user.isActive ? 'Active' : 'Inactive';
}