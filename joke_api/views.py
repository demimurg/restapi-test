import requests
import json
from flask import request, g, abort

from joke_api import app, db
from joke_api.models import (
    Joke, User, Log,
    joke_schema, user_schema
)


# Fake register/auth. Parsed from query param "login="
@app.before_request
def auth():
    query_login = request.args.get("login")
    if query_login is None:
        abort(app.response_class(
            response=json.dumps({"error": "login required"}),
            status=403,
            mimetype='application/json'
        ))

    user = db.session.query(User)\
        .filter_by(login=query_login).first()
    if user is None:
        user = User(login=query_login)
        db.session.add(user)
        db.session.commit()

    g.user = user


@app.after_request
def logging(response):
    try:
        log = Log(
            user_id=g.user.id,
            ip_addr=request.remote_addr,
        )

        db.session.add(log)
        db.session.commit()
    except AttributeError:
        pass

    return response


@app.route('/api/v1/jokes', methods=["GET", "POST"])
def jokes():
    if request.method == "GET":
        return {
            "user": user_schema.dump(g.user),
            "jokes": [
                joke_schema.dump(j)
                for j in g.user.jokes
            ]
        }, 200

    validate_joke(request.form)

    new_joke = Joke(content=request.form["joke"])
    g.user.jokes.append(new_joke)
    db.session.add(g.user)
    db.session.commit()

    return {
        "user": user_schema.dump(g.user),
        "joke": joke_schema.dump(new_joke)
    }, 201


@app.route("/api/v1/jokes/<int:id>", methods=["GET", "DELETE", "PUT"])
def specific_joke(id):
    for joke in g.user.jokes:
        if joke.id == id:
            if request.method == "DELETE":
                db.session.delete(joke)
                db.session.commit()
            elif request.method == "PUT":
                validate_joke(request.form)

                joke.content = request.form["joke"]
                db.session.add(joke)
                db.session.commit()

            return {
                "user_id": g.user.id,
                "joke": joke_schema.dump(joke)
            }, 200

    return {
        "error": "You have no joke with id %d" % id
    }, 404


@app.route('/api/v1/jokes/random', methods=["GET"])
def random_joke():
    res = requests.get("https://api.chucknorris.io/jokes/random")
    api_data = res.json()
    api_data["joke"] = api_data.pop("value")
    validate_joke(api_data)

    new_joke = Joke(content=api_data["joke"])
    g.user.jokes.append(new_joke)

    db.session.add(g.user)
    db.session.commit()

    return {
        "user_id": g.user.id,
        "joke": joke_schema.dump(new_joke)
    }, 200


def validate_joke(body):
    err = None
    if "joke" not in body:
        err = "Body have no field <joke>"
    elif body['joke'].isdigit() or body['joke'] == "None":
        err = "Wrong type for joke. Must be string"
    elif len(body["joke"]) == 0:
        err = "Joke is empty"

    if err:
        abort(app.response_class(
            response=json.dumps({"error": err}),
            status=400,
            mimetype='application/json'
        ))