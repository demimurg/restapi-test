from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "postgresql://%s:%s@%s:5432/%s" %\
    (os.getenv("PSQL_USER"), os.getenv("PSQL_PASS"),
    os.getenv("PSQL_HOST", "localhost"), os.getenv("PSQL_DB"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    # db.drop_all()
    db.create_all()

import joke_api.models
import joke_api.views
