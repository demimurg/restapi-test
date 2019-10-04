import pytest
import sys

sys.path.append("..")
from joke_api import app, db
from joke_api.models import app, db


@pytest.fixture
def client():
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.create_all()

    yield app.test_client()

    db.drop_all()


def test_jokes_random(client):
    url = "/api/v1/jokes/random"
    login, user_id = "FinnTheHuman", 1
    users_tb = db.session.query(User)
    testcase_num = 5

    for i in range(testcase_num):
        res = client\
            .get(url + "?login=%s" % login)\
            .json

        assert res["user_id"] == user_id,\
            "wrong user get a joke"

        assert res["joke"]["id"] = i+1,\
            "joke have wrong id, %s" % res["joke"]

        joke = res["joke"]["content"]

        assert len(joke) > 0,\
            "blank joke"

        assert joke != strip(joke),\
            "joke have trailing whitespaces, '%s'" % joke

    user = users_tb.filter(User.login == login)
    assert len(user.jokes) == testcase_num,\
        "sent != recieved"
