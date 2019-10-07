import pytest
import sys

sys.path.append("..")
from joke_api import app, db
from joke_api.models import User, Joke


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
    users_table = db.session.query(User)
    testcase_num = 5

    for i in range(testcase_num):
        res = client.get(url + "?login=%s" % login)

        assert res.status_code == 200,\
            "status code signals problem"

        body = res.json

        assert body["user_id"] == user_id,\
            "wrong user get a joke"

        assert body["joke"]["id"] == i+1,\
            "joke have wrong id"

        assert body["joke"]["content"] == body["joke"]["content"].strip(),\
            "joke have trailing whitespaces"

    user = users_table.filter(User.login == login).first()
    assert len(user.jokes) == testcase_num,\
        "sent != recieved"


def test_jokes(client):
    url = "/api/v1/jokes"
    login, user_id = "JakeTheDog", 1
    users_table = db.session.query(User)

    cases = [
        "I own the world's worst thesaurus. Not only is it awful, it's awful.",
        "Parenthood is feeding the mouth that bites you.",
        "Artificial intelligence is no match for natural stupidity.",
        "Filthy, stinking rich; well, two out of three ain't bad."
    ]

    # TEST POST
    for j in cases:
        res = client.post(
            url+"?login=%s" % login,
            data={"joke": j}
        )

        assert res.status_code == 201,\
            "[POST] wrong status code"

        body = res.json

        assert "user" in body and "joke" in body\
            and "id" in body["user"]\
            and "login" in body["user"]\
            and "id" in body["joke"]\
            and "content" in body["joke"],\
            "[POST] responce schema is invalid"

        assert body["user"]["id"] == user_id,\
            "[POST] wrong user get a joke"

    user = users_table.filter(User.login == login).first()
    assert [j.content for j in user.jokes] == cases,\
        "[POST] sent != recieved"

    # TEST GET
    res = client.get(url+"?login=%s" % login)

    assert res.status_code == 200,\
        "[GET] wrong status code"

    body = res.json

    assert [j["content"] for j in body["jokes"]] == cases,\
        "[GET] wrong collection of jokes returned"

    assert body["user"]["id"] == user_id and body["user"]["login"] == login,\
        "[GET] wrong user returned"


def test_jokes_id(client):
    base_url = "/api/v1/jokes"
    login, user_id = "IceKing", 1

    cases = ["not funny joke", "not realy funny joke"]
    for j in cases:
        client.post(
            base_url+"?login=%s" % login,
            data={"joke": j}
        )

    # TEST GET
    res = client.get(base_url+"/1"+"?login=%s" % login)

    assert res.status_code == 200,\
        "[GET] wrong status code"

    body = res.json
    assert "user_id" in body and "joke" in body\
        and "id" in body["joke"]\
        and "content" in body["joke"]\
        and body["user_id"] == user_id\
        and body["joke"]["content"] == cases[0],\
        "[GET] responce is invalid"

    # TEST PUT
    red_n, red_text = len(cases)-1, "very funny joke"
    url = base_url+"/%d" % red_n
    res = client.put(
        url+"?login=%s" % login,
        data={"joke": red_text}
    )

    assert res.status_code == 200,\
        "[PUT] wrong status code"

    jokes_tb = db.session.query(Joke)
    j = jokes_tb.filter(Joke.id == red_n).first()
    assert j.content == red_text,\
        "[PUT] update joke not working"

    users_tb = db.session.query(User)
    u = users_tb.filter(User.login == login).first()
    assert j in u.jokes,\
        "[PUT] user joke haven't been updated"

    # TEST DELETE
    res = client.delete(url+"?login=%s" % login)

    assert res.status_code == 200,\
        "[DELETE] wrong status code"

    jokes_tb = db.session.query(Joke)
    j = jokes_tb.filter(Joke.id == red_n).first()
    assert j is None,\
        "[DELETE] joke wasn't deleted from db"

    users_tb = db.session.query(User)
    u = users_tb.filter(User.login == login).first()
    assert red_text not in [j.content for j in u.jokes],\
        "[DELETE] joke wasn't deleted from user.jokes"

    # WRONG ID
    for method in ["GET", "PUT", "DELETE"]:
        req = getattr(client, method.lower())
        res = req(base_url+"/666?login=%s" % login)

        assert res.status_code == 404,\
            "jokes table haven't joke with id=666"
        assert res.json["error"] == "You have no joke with id 666"


def test_invalid_joke(client):
    login = "BMO"

    routes_methods = [
        ("/api/v1/jokes", "POST"),
        ("/api/v1/jokes/1", "PUT")
    ]

    # For correct work of PUT/update operation
    res = client.post(
        "/api/v1/jokes?login=%s" % login,
        data={"joke": "some joke"}
    )
    assert res.status_code == 201

    for r, m in routes_methods:
        req = getattr(client, m.lower())

        res = req(r+"?login=%s" % login, data={"Charli": "Kaufman"})
        assert res.status_code == 400\
            and res.json["error"] == "Body have no field <joke>"

        res = req(r+"?login=%s" % login, data={"joke": 124})
        assert res.status_code == 400\
            and res.json["error"] == "Wrong type for joke. Must be string"

        res = req(r+"?login=%s" % login, data={"joke": ""})
        assert res.status_code == 400\
            and res.json["error"] == "Joke is empty"


def test_auth_errors(client):
    # api request without login must raise error
    res = client.get("/api/v1/jokes")

    assert res.status_code == 403\
        and res.json["error"] == "Login required"
