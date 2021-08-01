from flask import make_response, jsonify, request
import json, datetime
from datetime import time, timedelta
from flask_restful import reqparse
from stackoverflow import db
from stackoverflow.models import User, Question, Answer, Comment
from stackoverflow.models_schema import UserSchema, QuestionSchema, AnswerSchema, CommentSchema
from stackoverflow.app import app
import jwt
from stackoverflow.utils import token_required, admin_required, check_user, check_answer_user, checkuser_comment
from flask_restful import  Resource


USER_ENDPOINT = "/api/users"
QUESTION_ENDPOINT = "/api/questions"
ANSWER_ENDPOINT = "/api/answers"
COMMENT_ENDPOINT = "/api/comments"

class UserRegistration(Resource):
    """Class having function for the registration of the user first time."""
    def post(self):
        request_data = request.get_json()
        username = request_data.get("username")
        email = request_data.get("email")
        role = request_data.get("role")

        if User.find_by_username(username):
            return {"details": f"User {username} already exists"}

        new_user = User(username=username, password=User.generate_hash(request_data.get("password")),
                        email=email, role=role)

        new_user.save()

        return {"details": "Your account is successfully created."}


class UserLogin(Resource):
    """Class having function for the login of the user to the application."""
    def post(self):
        request_data = request.get_json()
        username = request_data.get("username")
        password = request_data.get("password")

        user = User.find_by_username(username)

        if not user:
            return {"details": f"User {username} does not exist."}

        payload = {
            "user_email": user.email,
            "exp": datetime.datetime.utcnow() + timedelta(minutes=120)
        }
        if User.verify_hash(password, user.password):
            token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

            return jsonify({"token": token})

        return {"details" : "Could not authenticate the user."}


class UserView(Resource):
    """To get list of all users for ADMIN role only."""
    @token_required
    @admin_required
    def get(self, *args, **kwargs):
        user_details = User.query.all()
        schema = UserSchema()
        user_json = UserSchema(many=True)
        return user_json.dump(user_details)


class UserResourceView(Resource):
    """To get details of specific user."""
    @token_required
    def get(self, *args, **kwargs):
        user = User.query.filter_by(id=self.id).one()
        print("user is", user)
        schema = UserSchema()
        return schema.dump(user)

    @token_required
    def patch(self, *args, **kwargs):
        """To update the attributes of the user except email."""
        user = User.query.filter_by(id=self.id).first()
        print("user is", user)
        if "username" in request.json:
            user.username = request.json["username"]
        if "role" in request.json:
            user.role = request.json["role"]
        if "email" in request.json:
            if user.email != request.json.get("email"):
                return jsonify({"details": "Email cannot be updated."})
        db.session.commit()
        schema = UserSchema()
        return schema.dump(user)

    @token_required
    def delete(self, *args, **kwargs):
        """To delete the user."""
        user = User.query.filter_by(id=self.id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User is successfully deleted"})


class QuestionListView(Resource):
    """GET and POST method for the Question model."""
    @token_required
    @admin_required
    def get(self, *args, **kwargs):
        """To get all the questions of the user by ADMIN only."""
        questions = Question.query.all()
        schema = QuestionSchema(many=True)
        return schema.dump(questions)

    @token_required
    def post(self, *args, **kwargs):
        """To create a question for the app."""
        request_data = request.get_json()
        ques = request_data.get("question", "")
        user = User.query.filter_by(id=self.id).first()
        question = Question(question=ques, asked_by=user.id)
        question.save()
        schema = QuestionSchema()
        return schema.dump(question)


class QuestionResource(Resource):
    @token_required
    def get(self, *args, **kwargs):
        """GET method to get the specific question with all the answers and the comments."""
        ques_id = kwargs.get("ques_id")
        ques = Question.query.filter_by(id=ques_id).first()
        return QuestionSchema().dump(ques)

    @token_required
    def put(self, *args, **kwargs):
        """PUT method to update a question."""
        ques_id = kwargs.get("ques_id")
        request_data = request.get_json()
        ques = Question.query.filter_by(id=ques_id).first()
        if check_user(self.id, ques_id):
            ques.question = request_data.get("question")
            db.session.commit()
            return jsonify({"details": "Question is updated."})
        else:
            return jsonify({"details": "You are not authorized to perform this action."})

    @token_required
    def delete(self, *args, **kwargs):
        """To delete the question."""
        ques_id = kwargs.get("ques_id")
        ques = Question.query.filter_by(id=ques_id).first()
        if check_user(self.id, ques_id):
            db.session.delete(ques)
            db.session.commit()
            return jsonify({"details": "Question is successfully deleted."})
        else:
            return jsonify({"details": "You are not authorized to perform this action."})


class AnswerListView(Resource):
    """To create an answer to the question."""
    @token_required
    def post(self, *args, **kwargs):
        request_data = request.get_json()
        ques_id = kwargs.get("ques_id")
        ques = Question.query.filter_by(id=ques_id).first()
        ans = request_data.get("answer", "")
        user = User.query.filter_by(id=self.id).first()
        answer = Answer(answer=ans, answer_by=user.id, ans_on_ques=ques.id)
        answer.save()
        schema = AnswerSchema()
        return schema.dump(answer)


class AnswerResource(Resource):
    @token_required
    @admin_required
    def put(self, *args, **kwargs):
        """To update the answer to the question."""
        ans_id = kwargs.get("ans_id")
        request_data = request.get_json()
        ans = Answer.query.filter_by(id=ans_id).first()
        updated_ans = request_data.get("answer", "")
        if check_answer_user(self.id, ans_id):
            ans.answer = request_data.get("answer", "")
            db.session.commit()
            return AnswerSchema().dump(ans)
        else:
            return jsonify({"details": "You are not authorize to perform this action."})

    @token_required
    def delete(self, *args, **kwargs):
        """To delete the answer to the question."""
        ans_id = kwargs.get("ans_id")
        ans = Answer.query.filter_by(id=ans_id).first()
        if check_answer_user(self.id, ans_id):
            db.session.delete(ans)
            db.session.commit()
            return jsonify({"details": "Answer is successfully deleted."})
        else:
            return jsonify({"details": "You are not authorized to perform this action."})


class CommentListView(Resource):
    @token_required
    def post(self, *args, **kwargs):
        """To post a comment to the answer."""
        request_data = request.get_json()
        ans_id = kwargs.get("ans_id")
        comment = Comment(comment=request_data.get("comment"), comment_on=ans_id, comment_by=self.id)
        comment.save()
        schema = CommentSchema()
        return schema.dump(comment)


class CommentResource(Resource):
    @token_required
    @admin_required
    def put(self, *args, **kwargs):
        """To update the comment to the answer"""
        comment_id = kwargs.get("comment_id")
        request_data = request.get_json()
        comment = Comment.query.filter_by(id=comment_id).first()
        updated_comment = request_data.get("comment", "")
        if checkuser_comment(self.id, comment_id):
            comment.comment = request_data.get("comment", "")
            db.session.commit()
            return CommentSchema().dump(comment)
        else:
            return jsonify({"details": "You are not authorize to perform this action."})

    @token_required
    def delete(self, *args, **kwargs):
        """To delete the comment to the answer."""
        comment_id = kwargs.get("comment_id")
        comment = Comment.query.filter_by(id=comment_id).first()
        if checkuser_comment(self.id, comment_id):
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"details": "Comment is successfully deleted."})
        else:
            return jsonify({"details": "You are not authorized to perform this action."})

