import requests
from flask import request

from joke_api import app, db
from joke_api.models import (
    Joke, User,
    joke_schema, user_schema
)


# Auth and registration. Stupid. I know
def get_user():
    query_login = request.args.get("login")

    user = db.session.query(User)\
        .filter_by(login=query_login).first()
    if user is None:
        user = User(login=query_login)
        db.session.add(user)
        db.session.commit()

    return user


@app.route('/api/v1/jokes', methods=["GET", "POST"])
def jokes():
    cur_user = get_user()

    if request.method == "GET":
        res = {
            "user": user_schema.dump(cur_user),
            "jokes": [
                joke_schema.dump(j)
                for j in cur_user.jokes
            ]
        }, 200

        return res

    new_joke = Joke(content=request.form["joke"])
    cur_user.jokes.append(new_joke)
    db.session.add(cur_user)
    db.session.commit()

    return {
        "user": user_schema.dump(cur_user),
        "joke": joke_schema.dump(new_joke)
    }, 201


@app.route("/api/v1/jokes/<int:id>", methods=["GET", "DELETE", "PUT"])
def specific_joke(id):
    cur_user = get_user()

    for joke in cur_user.jokes:
        if joke.id == id:
            if request.method == "DELETE":
                db.session.delete(joke)
                db.session.commit()
            elif request.method == "PUT":
                joke.content = request.form["joke"]
                db.session.add(joke)
                db.session.commit()

            return {
                "user_id": cur_user.id,
                "joke": joke_schema.dump(joke)
            }, 200

    return {
        "error": "you have no joke with id %d" % id
    }, 404


@app.route('/api/v1/jokes/random', methods=["GET"])
def random_joke():
    res = requests.get("https://api.chucknorris.io/jokes/random")
    api_data = res.json()
    new_joke = Joke(content=api_data["value"])

    cur_user = get_user()
    cur_user.jokes.append(new_joke)

    db.session.add(cur_user)
    db.session.commit()

    return {
        "user_id": cur_user.id,
        "joke": joke_schema.dump(new_joke)
    }, 200