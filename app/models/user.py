from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  # store hashed password
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
