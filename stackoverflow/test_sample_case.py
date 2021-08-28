from stackoverflow.app import app
import pytest
from stackoverflow.models import User
from flask import request
from flask.testing import FlaskClient
from stackoverflow.utils import generate_token

# class CustomClient(FlaskClient):
#     def __init__(self, *args, **kwargs):
#         self._authentication = kwargs.pop("authentication")
#         super(CustomClient, self).__init__(*args, **kwargs)


@pytest.fixture
def client():
    app.testing = True
    client_test = app.test_client()
    return client_test

@pytest.fixture
def get_token(client):
    json_data = {
        "username" : "heena",
        "password": "Test@1234"
    }
    with app.app_context():
        token = generate_token(json_data.get("username"), json_data.get("password"))
    yield token

def test_user(client, get_token):
    token = "Bearer " + get_token
    resp = client.get("/api/users", headers={"Authorization": token})
    assert isinstance(resp.json, dict)
    assert resp.status_code == 200

def test_signup(client):
    resp = client.post("/api/users/signup", json={"username":"heena91", "email":"heena91@gmail.com",
                                                  "password": "Test@123", "role": "admin"})
    json_data = resp.get_json()
    assert resp.status_code == 200
    assert "Your account is successfully created." in resp.json.get("details")


def test_login(client):
    resp = client.post("/api/users/login", json={"username": "heena", "password": "Test@1234"})
    # print(token)
    assert resp.status_code == 200

def test_question(client, get_token):
    token = "Bearer " + get_token
    resp = client.post("/api/questions", json={"question": "what is the next question?"}, headers={"Authorization": token})
    assert resp.status_code == 200
