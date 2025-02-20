import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorites
import json

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    users = User.query.all()
    usersList = list(map(lambda obj: obj.serialize(), users))
    response_body = {
        "results": usersList
    }
    return jsonify(response_body), 200

@app.route('/user/<int:id>', methods=['GET'])
def handle_singleuser(id):
    user_id = User.query.get(id)
    user = user_id.serialize()
    response_body = {
        "results": user
    }
    return jsonify(response_body), 200

@app.route('/characters', methods=['GET'])
def handle_characters():
    characters = Characters.query.all()
    charactersList = list(map(lambda obj: obj.serialize(), characters))
    response_body = {
        "results": charactersList
    }
    return jsonify(response_body), 200

@app.route('/characters/<int:id>', methods=['GET'])
def handle_singlecharacters(id):
    characters_id = Characters.query.get(id)
    characters = characters_id.serialize()
    response_body = {
        "results": characters
    }
    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    planetsList = list(map(lambda obj: obj.serialize(), planets))
    response_body = {
        "results": planetsList
    }
    return jsonify(response_body), 200

@app.route('/planets/<int:id>', methods=['GET'])
def handle_singleplanets(id):
    planets_id = Planets.query.get(id)
    planets = planets_id.serialize()
    response_body = {
        "results": planets
    }
    return jsonify(response_body), 200

@app.route('/favorites', methods=['GET'])
def handle_favorites():
    favorites = Favorites.query.all()
    favoritesList = list(map(lambda obj: obj.serialize(), favorites))
    response_body = {
        "results": favoritesList
    }
    return jsonify(response_body), 200

@app.route('/favorites/<int:id>', methods=['GET'])
def handle_singlefavorites(id):
    favorites_id = Favorites.query.get(id)
    favorites = favorites_id.serialize()
    response_body = {
        "results": favorites
    }
    return jsonify(response_body), 200

@app.route('/users/favorites', methods=['GET'])
def handle_singleallfavorites():
    favorites = User.query.all()
    allfavorites = list(map(lambda favorites: favorites.serialize(), favorites))
    response_body = {
        "results": allfavorites
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/<int:id>', methods=['GET'])
def handle_singleuserfavorites(id):
    favorites_id = User.query.get(id)
    favorites = favorites_id.serialize()
    response_body = {
        "results": favorites
    }
    return jsonify(response_body), 200

@app.route('/user/<int:id>', methods=['POST'])
def handle_addfavorites(id):
    body = json.loads(request.data)
    favorites = Favorites(user_id=body["user_id"], characters_id=body["characters_id"], planets_id=body["planets_id"])
    db.session.add(favorites)
    db.session.commit()
    response_body = {
        "results": "Favorite was successfully added"
    }
    return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/characters/<int:character_id>', methods=['POST'])
def handle_favCharacter(character_id, user_id):
    character = Favorites.query.filter_by(characters_id=character_id, user_id=user_id).first()
    if character:
        return jsonify({"result": "favorite already exists"})
    else:
        favCharacter = Favorites(user_id=user_id, characters_id=character_id)
        db.session.add(favCharacter)
        db.session.commit()
        response_body = {"results": "Favorite added"}
        return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
def handle_favPlanet(planet_id, user_id):
    planet = Favorites.query.filter_by(planets_id=planet_id, user_id=user_id).first()
    if planet:
        return jsonify({"result": "favorite already exist"})
    else:
        favPlanet = Favorites(user_id=user_id, planets_id=planet_id)
        db.session.add(favPlanet)
        db.session.commit()
        response_body = {
            "results": "Favorite added"
        }
        return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/characters/<int:character_id>', methods=['DELETE'])
def handle_deleteCharacter(character_id, user_id):
    favorite = Favorites.query.filter_by(user_id=user_id).filter_by(characters_id=character_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        response_body = {"results": "Favorite was removed"}
        return jsonify(response_body), 200
    else:
        return jsonify({"result": "favorite not found"})


@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def handle_deletePlanet(planet_id, user_id):
    favorite = Favorites.query.filter_by(user_id=user_id).filter_by(planets_id=planet_id).first()
    if Favorites:
        db.session.delete(favorite)
        db.session.commit()
        response_body = {
            "results": "Favorite was removed"
        }
        return jsonify(response_body), 200
    else:
        return jsonify({"result": "favorite not found"})

@app.route('/user/<int:id>/favorites/<int:user_id>', methods=['DELETE'])
def handle_(id, user_id):
    favorite = Favorites.query.filter_by(id=user_id).all()
    db.session.delete(favorite[1])
    db.session.commit()
    response_body = {
        "results": "Favorite was removed"
    }
    return jsonify(response_body), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
