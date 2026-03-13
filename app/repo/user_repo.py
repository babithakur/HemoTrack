from app import db
from app.models.user import User

class UserRepo:
    @staticmethod
    def create_user(name, email, password, gender, dob):
        user = User(name=name, email=email, password=password, gender=gender, dob=dob)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def update_user(user):
        db.session.commit()
        return user
