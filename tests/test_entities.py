import unittest
import sys
import requests
import json

sys.path.append("..")
from joke_api import app, db

base_url = "/api/v1"


class JokesViewTests(unittest.TestCase):
    url = base_url + "/jokes"
    login = "?login=FinnTheHuman"

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.create_all()

        self.app = app.test_client()

    def tearDown(self):
        db.drop_all()

    def test_basic(self):
        dataset_len = 5

        for _ in range(dataset_len):
            joke_obj = requests\
                .get("https://api.chucknorris.io/jokes/random")\
                .content
            joke_val = json.loads(joke_obj)["value"]

            res = self.app.post(
                self.url + self.login,
                data={"joke": joke_val}
            )

            self.assertEqual(
                res.status_code, 201,
                "Joke isn't created"
            )

            db_obj = json.loads(res.data)
            self.assertEqual(
                joke_val, db_obj["joke"]["content"],
                "Source not equal db repr"
            )

            self.assertIn(
                db_obj["user"]["login"], self.login,
                "Post to wrong login"
            )

        res = self.app.get(self.url + self.login)
        db_obj = json.loads(res.data)

        self.assertEqual(
            len(db_obj["jokes"]), dataset_len,
            "User haven't all jokes"
        )


if __name__ == '__main__':
    unittest.main()
