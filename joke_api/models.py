from flask_marshmallow import Marshmallow
from joke_api import app, db


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


ma = Marshmallow(app)


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
