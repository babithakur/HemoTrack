import re
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app.repo.user_repo import UserRepo
from flask import session

class UserService:
    @staticmethod
    def validate_input(email, password, confirm_password, name=None, gender=None, dob=None):
        if not name:
            raise ValueError("Please enter your name.")

        if not email or not password or not confirm_password:
            raise ValueError("Email and password are required")

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        pw_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pw_regex, password):
            raise ValueError(
                "Password must be at least 8 characters long, "
                "include uppercase, lowercase, number, and special character"
            )
        if not dob:
            raise ValueError("Date of birth is required")
        try:
            dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format for date of birth. Use YYYY-MM-DD")
        
        #minimum age check (18 years)
        today = date.today()
        age = today.year - dob_parsed.year - ((today.month, today.day) < (dob_parsed.month, dob_parsed.day))
        if age < 18:
            raise ValueError("You must be at least 18 years old to register")
        
        if not gender:
            raise ValueError("Gender is required")
        if gender.lower() not in ["male", "female"]:
            raise ValueError("Invalid gender selection")

        return True

    @staticmethod
    def register_user(email, password, confirm_password, name=None, gender=None, dob=None):
        UserService.validate_input(email, password, confirm_password, name, gender, dob)
        existing_user = UserRepo.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        hashed_pw = generate_password_hash(password)
        return UserRepo.create_user(name, email, hashed_pw, gender, dob)
    
    @staticmethod
    def login_user(email, password, remember_me):
        user = UserRepo.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not check_password_hash(user.password, password):
            raise ValueError("Invalid email or password")

        session["user_id"] = user.user_id
        session["email"] = user.email
        session["name"] = user.name
        if remember_me:
            session.permanent = True
        else:
            session.permanent = False
        return user
