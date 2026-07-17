users = [
    {"id": 1, "name": "Chhaileang", "email": "chhaileang@test.com", "role": "admin", "isActive": True},
    {"id": 2, "name": "Chhey Lyheng", "email": "lyheng@test.com", "role": "customer", "isActive": True},
    {"id": 3, "name": "Vann Sak", "email": "sak@test.com", "role": "customer", "isActive": True},
    {"id": 4, "name": "Chey Kimrith", "email": "kimrith@test.com", "role": "owner", "isActive": True},
    {"id": 5, "name": "Som Dara", "email": "dara@test.com", "role": "customer", "isActive": False}
]

products = [
    {"id": 101, "name": "Standard Room", "category": "Room", "price": 25.0, "stock": 10},
    {"id": 102, "name": "Deluxe Room", "category": "Room", "price": 45.0, "stock": 5},
    {"id": 103, "name": "Suite", "category": "Room", "price": 80.0, "stock": 2},
    {"id": 104, "name": "Coffee", "category": "Drink", "price": 2.5, "stock": 100},
    {"id": 105, "name": "Club Sandwich", "category": "Food", "price": 5.5, "stock": 50}
]

orders = [
    {"id": 1001, "userId": 2, "productId": 101, "quantity": 1, "status": "pending", "createdAt": "2026-07-18T10:00:00Z"},
    {"id": 1002, "userId": 3, "productId": 102, "quantity": 1, "status": "confirmed", "createdAt": "2026-07-18T11:30:00Z"},
    {"id": 1003, "userId": 5, "productId": 104, "quantity": 2, "status": "completed", "createdAt": "2026-07-18T12:00:00Z"},
    {"id": 1004, "userId": 2, "productId": 105, "quantity": 1, "status": "rejected", "createdAt": "2026-07-18T13:15:00Z"},
    {"id": 1005, "userId": 3, "productId": 101, "quantity": 1, "status": "pending", "createdAt": "2026-07-18T14:00:00Z"}
]