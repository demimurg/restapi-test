import pytest
import sys
import requests
import json

sys.path.append("..")
from joke_api import app, db

base_url = "/api/v1"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.create_all()

    yield app.test_client()

    db.drop_all()


def test_jokes(client):
    url = base_url + "/jokes"
    login = "?login=FinnTheHuman"

    added_jokes = []
    for _ in range(5):
        joke_obj = requests\
            .get("https://api.chucknorris.io/jokes/random")\
            .json()
        joke_val = json.loads(joke_obj).value

        res = client.post(url + login, data={
            "joke": joke_val
        })

        db_joke = json.loads(res.get_json())
        assert joke_val == db_joke.content

        added_jokes.append(db_joke)

    res = client.get(url + login)
    assert res.status_code == 200

    print(added_jokes, res.get_json())
