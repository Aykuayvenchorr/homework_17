# app.py

from flask import Flask, request, json, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Str()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        movies_schema = MovieSchema(many=True)
        if director_id and genre_id:
            movie_dg = db.session.query(Movie).filter(Movie.genre_id == genre_id,
                                                      Movie.director_id == director_id).all()
            if movie_dg is None:
                return 'incorrect id', 404  # Возвращает [] , а не incorrect id
            return movies_schema.dump(movie_dg)
        elif director_id:
            movie_dir = db.session.query(Movie).filter(Movie.director_id == director_id).all()
            if movie_dir is None:
                return 'incorrect id', 404  # Возвращает [] , а не incorrect id
            return movies_schema.dump(movie_dir)
        elif genre_id:
            movie_gen = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
            if movie_gen is None:
                return 'incorrect id', 404  # Возвращает [] , а не incorrect id
            return movies_schema.dump(movie_gen)

        all_movies = Movie.query.all()
        return movies_schema.dump(all_movies)

    def post(self):
        req_json = request.json
        db.session.add(Movie(**req_json))
        db.session.commit()
        return 'ok', 200


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie_schema = MovieSchema()
        movie = Movie.query.get(uid)
        if movie is None:
            return 'incorrect id', 404
        return movie_schema.dump(movie)

    def put(self, uid):
        req_json = request.json
        db.session.query(Movie).filter(Movie.id == uid).update(req_json)
        db.session.commit()
        return 'ok', 204

    def delete(self, uid):
        movie = db.session.query(Movie).get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "ok", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        director_schema = DirectorSchema()
        directors_schema = DirectorSchema(many=True)
        result = db.session.query(Director).all()
        return directors_schema.dump(result)

    def post(self):
        req_json = request.json
        db.session.add(Director(**req_json))
        db.session.commit()
        return 'ok', 200


@director_ns.route('/<int:uid>')
class DirectorsView(Resource):
    def get(self, uid):
        director_schema = DirectorSchema()
        result = db.session.query(Director).get(uid)
        return director_schema.dump(result)

    def put(self, uid):
        director = db.session.query(Director).get(uid)
        req_json = request.json
        # director_new = Director(**req_json)
        # director.id = director_new.id
        # director.name = director_new.name

        db.session.query(Director).filter(Director.id == uid).update(req_json)

        db.session.commit()
        return 'ok', 204

    def delete(self, uid):
        director = db.session.query(Director).get(uid)
        db.session.delete(director)
        db.session.commit()
        return "ok", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genre_schema = GenreSchema()
        genres_schema = GenreSchema(many=True)
        result = db.session.query(Genre).all()
        return genres_schema.dump(result)

    def post(self):
        req_json = request.json
        db.session.add(Genre(**req_json))
        db.session.commit()
        return 'ok', 200


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        genre_schema = GenreSchema()
        result = db.session.query(Genre).get(uid)
        return genre_schema.dump(result)

    def put(self, uid):
        genre = db.session.query(Genre).get(uid)
        req_json = request.json
        db.session.query(Genre).filter(Genre.id == uid).update(req_json)
        db.session.commit()
        return 'ok', 204

    def delete(self, uid):
        genre = db.session.query(Genre).get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "ok", 204


if __name__ == '__main__':
    app.run(debug=True)
