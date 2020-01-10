import requests
from collections import namedtuple
from flask import request, g, abort, json
from joke_api import app, db
from joke_api.models import (
    Joke, User, Log,
    joke_schema, user_schema
)


@app.before_request
def authorization():
    auth = request.authorization
    if auth is None or auth.username == "":
        abort(app.response_class(
            response=json.dumps({"error": "Login required"}),
            status=403,
            mimetype='application/json'
        ))

    user = db.session.query(User)\
        .filter_by(login=auth.username).first()
    if user is None:
        user = User(login=auth.username)
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
    ApiObj = namedtuple("ApiObj", ["source", "wrapper"])
    # wrapper need to prepare form for validation
    ext_api, that_works = [
        ApiObj(
            "https://api.chucknorris.io/jokes/random",
            lambda res: {"joke": res.json()["value"]}
        ),
        ApiObj(
            "http://api.icndb.com/jokes/random",
            lambda res: {"joke": res.json()["value"]["joke"]}
        )
    ], 0

    api_data = None
    while api_data is None:
        try:
            api = ext_api[that_works]
            res = requests.get(api.source)
            api_data = api.wrapper(res)
        except Exception as err:
            print("API (%s) ERROR: %s" % (api.source, err))
            that_works += 1

            if that_works == len(ext_api):
                return {
                    "error": "External API for random jokes aren't working",
                }, 500

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
    """Causes abort if error"""

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
