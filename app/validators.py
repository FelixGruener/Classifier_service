from app.models import User
import re
from app import db
from flask import jsonify
from flask_jwt_extended import create_access_token

class RegistrationValidator:

    @classmethod
    def registration_validator(cls, username, email, password1, password2):
        if cls.username_is_unique_and_valid(username):
            if cls.email_is_unique_and_valid(email):
                if cls.password_match(password1, password2):
                    return True, "Data is valid"
                else:
                    return False, "passwords must be the same"
            else:
                return False, "email already exist"
        else:
            return False, "Username already exist"

    @classmethod
    def email_is_unique_and_valid(cls, email):
        return db.session.query(User.id).filter_by(email=email).scalar() is None
    
    @classmethod
    def username_is_unique_and_valid(cls, username):
        return db.session.query(User.id).filter_by(username=username).scalar() is None
    
    @staticmethod
    def password_match(password1, password2):
        return password1 == password2 and password1 is not None or password2 is not None


class AuthValidator:

    @staticmethod
    def validate_user(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True
        else:
            return False
    
    @staticmethod
    def authenticate(username):
        return create_access_token(identity=username)