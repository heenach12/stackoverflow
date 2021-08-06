#!/usr/bin/env bash

export FLASK_APP=stackoverflow/app.py

flask db init
flask db migrate
flask db upgrade

flask run --host=0.0.0.0