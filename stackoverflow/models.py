import uuid, datetime
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Table, Text, Boolean
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import desc
from stackoverflow import db


vote_answer = db.Table("vote_answer",
                    Column("answer_id", ForeignKey("answers.id"), primary_key=True),
                    Column("user_id", ForeignKey("users.id"), primary_key=True))


class User(db.Model):
    """Model for saving User attributes."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(250), nullable=False)
    questions = relationship("Question", back_populates="user", cascade="all, delete", passive_deletes=True)
    answers = relationship("Answer", back_populates = "user", cascade="all, delete", passive_deletes=True)
    comments = relationship("Comment", back_populates = "user", cascade="all, delete, delete-orphan", passive_deletes=True)
    voted_ans = relationship("Answer", secondary=vote_answer, back_populates = "voted_by")
    role = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=True)

    def __str__(self):
        return self.username

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash_):
        return sha256.verify(password, hash_)


class Comment(db.Model):
    """Model for saving the comments on the answers of the question."""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment = Column(Text)
    comment_on = Column(UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"))
    comment_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    answers = relationship("Answer", back_populates = "comments")
    comment_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    user = relationship("User", back_populates = "comments")

    def __str__(self):
        return self.comment

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Answer(db.Model):
    """Model for saving answers of the question."""
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer = Column(Text)
    answer_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    answer_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    user = relationship("User", back_populates = "answers")
    ans_on_ques = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"))
    ques = relationship("Question", back_populates="answers")
    comments = relationship("Comment", back_populates="answers", order_by=(desc(Comment.comment_timestamp)), cascade="all, delete, delete-orphan", passive_deletes=True)
    voted_by = relationship("User", secondary=vote_answer, back_populates="voted_ans", passive_deletes=True)
    votes = Column(Integer, default=0)
    isvoted = Column(Boolean, default=False)

    def __str__(self):
        return self.answer

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Question(db.Model):
    """Model for saving the question."""
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text)
    asked_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    asked_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    user = relationship("User", back_populates = "questions")
    answers = relationship("Answer", back_populates = "ques", order_by=(desc(Answer.answer_timestamp)),
                            cascade="all, delete, delete-orphan", passive_deletes=True )

    def __str__(self):
        return self.question

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
