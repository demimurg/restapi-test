import unittest
import sys

sys.path.append("..")
from joke_api import app, db


@pytest.fixture(autouse=True)
def client():
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.create_all()
    return app.test_client()


class TestJokes():
    url = "/api/v1/jokes"

    def test_random(self, client):
        res = client.get(self.url + "/random" + "?login=finn")

        assert res.status_code == 200
