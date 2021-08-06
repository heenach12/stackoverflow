from marshmallow import Schema, fields, post_load, post_dump, ValidationError, validate
from stackoverflow.models import User, Question, Answer, Comment
from marshmallow_dataclass import dataclass
# from stackoverflow.app import app
from flask_marshmallow import Marshmallow


# ma = Marshmallow(app)

class UserSchema(Schema):
    """Schema for the User Model."""
    id = fields.UUID()
    username = fields.String()
    email = fields.Email()
    role = fields.String()
    is_active = fields.Boolean()

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "is_active")


class CommentSchema(Schema):
    """Schema for the Comments Model"""
    id = fields.UUID()
    comment = fields.String()
    user = fields.Nested(UserSchema(only=("username",)))
    comment_timestamp = fields.DateTime()
    answers = fields.Nested("AnswerSchema", only=("id", "answer",))

    class Meta:
        model = Comment
        fields = ("id", "comment", "user", "comment_timestamp", "answers")


class AnswerSchema(Schema):
    """Schema for the Answer Model."""
    id = fields.UUID()
    answer = fields.String()
    answer_timestamp = fields.DateTime()
    user = fields.Nested(UserSchema(only=("id", "username")))
    ques = fields.Nested("QuestionSchema", only=("id", "question",))
    comments = fields.List(fields.Nested("CommentSchema", only=("comment", "comment_timestamp")))

    class Meta:
        model = Answer
        fields = ("id", "answer", "answer_timestamp", "ques", "user", "comments")


class QuestionSchema(Schema):
    """Schema for the Question Model."""
    id = fields.UUID()
    question = fields.String()
    asked_timestamp = fields.DateTime()
    user = fields.Nested(UserSchema(only=("id", "username")))
    answers = fields.List(fields.Nested("AnswerSchema", exclude=("ques",)))

    class Meta:
        model = Question
        fields = ("id", "question", "asked_timestamp", "user", "answers")

