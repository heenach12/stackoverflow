import os

class Config():
    DEBUG = True

class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Innovation12@database:5432/stackoverflow2"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Innovation12@localhost:5432/stackoverflow"


config_settings = {
    "development" : DevelopmentConfig
}

