"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorites
import json
#from models import Person

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
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

@app.route('/user/favorites/<int:id>', methods=['GET'])
def handle_singleuserfavorites(id):
    favorites_id = User.query.get(id)
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

@app.route('/user/<int:id>', methods=['POST'])
def handle_addfavorites(id):
    body = json.loads(request.data)
    favorites = Favorites(user_id=body["user_id"], characters_id=body["characters_id"], planets_id=body["planets_id"])
    db.session.add(favorites)
    db.session.commit()
    response_body = {
        "results": "Favourite was successfully added"
    }
    return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/people/<int:people_id>', methods=['POST'])
def handle_favPeople(people_id, user_id):
    people = Favorites.query.filter_by(characters_id=people_id).filter_by(user_id=user_id)
    if people:
        return jsonify({"result": "favourite already exist"})
    else:
        favPeople = Favorites(user_id=user_id, characters_id=people_id)
        db.session.add(favPeople)
        db.session.commit()
        response_body = {
            "results": "Favourite added"
        }
        return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
def handle_favPlanet(planet_id, user_id):
    planet = Favorites.query.filter_by(planets_id=planet_id).filter_by(user_id=user_id)
    if planet:
        return jsonify({"result": "favourite already exist"})
    else:
        favPlanet = Favorites(user_id=user_id, planets_id=planet_id)
        db.session.add(favPlanet)
        db.session.commit()
        response_body = {
            "results": "Favourite added"
        }
        return jsonify(response_body), 200

@app.route('/user/<int:user_id>/favorites/people/<int:people_id>', methods=['DELETE'])
def handle_deletePeople(people_id, user_id):
    favourite = Favorites.query.filter_by(user_id=user_id).filter_by(characters_id=people_id).first()
    if Favorites:
        db.session.delete(favourite)
        db.session.commit()
        response_body = {
            "results": "Favourite was removed"
        }
        return jsonify(response_body), 200
    else:
        return jsonify({"result": "favourite not found"})

@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def handle_deletePlanet(planet_id, user_id):
    favourite = Favorites.query.filter_by(user_id=user_id).filter_by(planets_id=planet_id).first()
    if Favorites:
        db.session.delete(favourite)
        db.session.commit()
        response_body = {
            "results": "Favourite was removed"
        }
        return jsonify(response_body), 200
    else:
        return jsonify({"result": "favourite not found"})

@app.route('/user/<int:id>/favorites/<int:user_id>', methods=['DELETE'])
def handle_(id, user_id):
    favourite = Favorites.query.filter_by(id=user_id).all()
    db.session.delete(favourite[1])
    db.session.commit()
    response_body = {
        "results": "Favourite was removed"
    }
    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
