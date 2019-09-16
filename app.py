from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://" +\
    "madma:mdma@localhost:5432/app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Joke(db.Model):
    __tablename__ = "jokes"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return "<Joke (id=%s, content=%s)>"\
            % (self.id, self.content)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)

    jokes = db.relationship("Joke", backref="user", lazy=True)

    def __repr__(self):
        return "<User (id=%s, login=%s)>"\
            % (self.id, self.login)


class JokeSchema(ma.ModelSchema):
    class Meta:
        model = Joke
        fields = ("id", "content")


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ("id", "login")


joke_schema = JokeSchema()
user_schema = UserSchema()


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
