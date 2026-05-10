import re
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app.repo.user_repo import UserRepo
from flask import session
import cv2
import numpy as np
from app.utils.conjunctiva_utils import (
    detect_and_crop_eyes, extract_conjunctiva_from_eye,
    preprocess_roi, extract_anemia_features,
    predict_anemia, average_features
)
from app.utils.image_to_base64 import image_to_base64

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
    
    @staticmethod
    def get_user_by_id(user_id):
        return UserRepo.get_user_by_id(user_id)

    @staticmethod
    def update_settings(user_id, name=None, current_password=None, new_password=None):
        user = UserRepo.get_user_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        if name and name.strip():
            user.name = name.strip()

        if new_password:
            if not current_password:
                raise ValueError("Current password is required")
            if not check_password_hash(user.password, current_password):
                raise ValueError("Current password is incorrect")
            pw_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.match(pw_regex, new_password):
                raise ValueError(
                    "Password must be at least 8 characters long, "
                    "include uppercase, lowercase, number, and special character"
                )
            hashed_pw = generate_password_hash(new_password)
            user.password = hashed_pw

        return UserRepo.update_user(user)
    
    @staticmethod
    def analyze_conjunctiva(image_path):
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Invalid image"}

        eyes = detect_and_crop_eyes(image)
        if not eyes:
            return {"error": "No eyes detected"}

        feature_list, scores, image_data = [], [], {}
        detected_eyes = []

        for idx, eye_data in enumerate(eyes):
            roi = extract_conjunctiva_from_eye(eye_data["eye"])
            preprocessed_roi = preprocess_roi(roi)

            # Encode images as base64
            eye_key = f"eye_{idx+1}"
            roi_key = f"roi_{idx+1}"
            pre_key = f"preprocessed_{idx+1}"

            image_data[eye_key] = image_to_base64(eye_data["eye"])
            image_data[roi_key] = image_to_base64(roi)
            image_data[pre_key] = image_to_base64(preprocessed_roi)

            # Add metadata for template looping
            detected_eyes.append({
                "eye_key": eye_key,
                "roi_key": roi_key,
                "pre_key": pre_key,
                "side": "Left" if idx == 0 else "Right"
            })

            features = extract_anemia_features(preprocessed_roi)
            if features and features["mean_value"] >= 80:
                prediction, score = predict_anemia(features)
                feature_list.append(features)
                scores.append(score)

        if not scores:
            return {"error": "No valid conjunctiva ROI"}

        avg_features = average_features(feature_list)
        final_score = float(np.mean(scores))
        if final_score >= 70:
            final_prediction = "High anemia likelihood"
        elif final_score >= 40:
            final_prediction = "Moderate anemia likelihood"
        else:
            final_prediction = "Low anemia likelihood"

        return {
            "features": avg_features,
            "score": round(final_score, 2),
            "prediction": final_prediction,
            "images": image_data,
            "detected_eyes": detected_eyes
        }



    

