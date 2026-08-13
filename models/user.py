from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    profile_img = db.Column(db.String(255), nullable=True, default='default_profile.png')
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    roles = db.Column(db.String(128), default="user")
    status = db.Column(db.String(32), default="active")