from stackoverflow.models import User, Question, Answer, Comment
from functools import wraps
# from stackoverflow.app import app
from flask import request, jsonify
import json, datetime
from datetime import time, timedelta

import jwt

def generate_token(username, password):
    # user = User.find_by_username(username)
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"details": f"User {username} does not exist."}

    payload = {
        "user_email": user.email,
        "exp": datetime.datetime.utcnow() + timedelta(minutes=120)
    }
    if User.verify_hash(password, user.password):
        token = jwt.encode(payload, "54b95540ea78f59c9f5877662f3075c5", algorithm="HS256")

        return token
    return None


def token_required(f):
    """Function for decoding the JWT token and checking the authentication of the user."""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        token = request.headers.get("Authorization")
        if token:
            if  "Basic" in token:
                return
            parts = token.split("Bearer ")
            if len(parts) != 2:
                raise Exception("Invalid token header")
            token = parts[1]
        else:
            return jsonify({'details': 'a valid token is missing'})
        payload=None
        try:
            payload = jwt.decode(token, "54b95540ea78f59c9f5877662f3075c5", algorithms=["HS256"])
            print("payload is", payload)
        except Exception:
            return jsonify({"details": "Token is expired or invalid, please login"})

        user = User.query.filter_by(email= payload["user_email"]).first()
        if user and user.is_active:
            return f(user, *args, **kwargs)
        else:
            return jsonify({"details": "User is not active"})

    return decorator


def admin_required(func):
    """Function to check if the user role is ADMIN."""
    def wrapper(self, *args, **kwargs):
        user = User.query.filter_by(id=self.id).first()
        if user.role == "ADMIN":
            return func(self,*args, **kwargs)
        else:
            return jsonify({"details": "User must be an admin to perform this action."})

    return wrapper


def check_user(user_id, ques_id):
    """Function to verify if user is admin or user of the question is same as to user updating/deleting the question."""
    user = User.query.filter_by(id=user_id).first()
    ques = Question.query.filter_by(id=ques_id).first()
    if ques.user == user or user.role == "ADMIN":
        return True
    else:
        return False


def check_answer_user(user_id, ans_id):
    """Function to verify if user is admin or user of the answer is same as to user updating/deleting the answer."""
    user = User.query.filter_by(id=user_id).first()
    ans = Answer.query.filter_by(id=ans_id).first()
    if ans.user == user or user.role == "ADMIN":
        return True
    else:
        return False

def checkuser_comment(user_id, comment_id):
    """Function to verify if user is admin or user of the comment is same as to user updating/deleting the comment."""
    user = User.query.filter_by(id=user_id).first()
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment.user == user or user.role == "ADMIN":
        return True
    else:
        return False
