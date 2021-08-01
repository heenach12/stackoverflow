from flask import Flask, g
from flask_marshmallow import Marshmallow
from stackoverflow.config import config_settings
from flask_sqlalchemy import SQLAlchemy
from stackoverflow import db
import jwt
from flask_restful import Api
from stackoverflow.views import UserView, UserResourceView, QuestionListView, QuestionResource, AnswerListView, \
    UserRegistration, AnswerResource, CommentResource, CommentListView, UserLogin, USER_ENDPOINT, QUESTION_ENDPOINT,\
    ANSWER_ENDPOINT, COMMENT_ENDPOINT

app = Flask(__name__)


app.config.from_object(config_settings["development"])
app.config["SECRET_KEY"] = "badf37c48027029de6d4a8b8c4741881"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "54b95540ea78f59c9f5877662f3075c5"

ma = Marshmallow(app)

api = Api(app)
api.add_resource(UserView, USER_ENDPOINT)
api.add_resource(UserResourceView, USER_ENDPOINT, f"{USER_ENDPOINT}/user")
api.add_resource(QuestionListView, QUESTION_ENDPOINT)
api.add_resource(QuestionResource, QUESTION_ENDPOINT, f"{QUESTION_ENDPOINT}/<uuid:ques_id>")
api.add_resource(AnswerListView, ANSWER_ENDPOINT, f"{ANSWER_ENDPOINT}/<uuid:ques_id>")
api.add_resource(AnswerResource, ANSWER_ENDPOINT, f"{ANSWER_ENDPOINT}/<uuid:ans_id>")
api.add_resource(CommentListView, COMMENT_ENDPOINT, f"{COMMENT_ENDPOINT}/<uuid:ans_id>")
api.add_resource(CommentResource, COMMENT_ENDPOINT, f"{COMMENT_ENDPOINT}/<uuid:comment_id>")
api.add_resource(UserRegistration, USER_ENDPOINT, f"{USER_ENDPOINT}/signup")
api.add_resource(UserLogin, USER_ENDPOINT, f"{USER_ENDPOINT}/login")

db.init_app(app)


if __name__=="__main__":
    app.run(debug=True)

