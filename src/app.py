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
from models import db, People, Planets, User
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

# Error handler
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Sitemap endpoint
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    people_JSON = [{'id': P.Id, 'Name': P.Name, 'Last_Name': P.Last_Name, 'Age': P.Age} for P in people_list]
    return jsonify(people_JSON), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    return jsonify({
        'id': person.Id,
        'Name': person.Name,
        'Last_Name': person.Last_Name,
        'Age': person.Age
    }), 200

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if not data or 'Name' not in data or 'Last_Name' not in data or 'Age' not in data:
        return jsonify({"error": "Faltan datos para crear un personaje"}), 400
    
    new_person = People(Name=data['Name'], Last_Name=data['Last_Name'], Age=data['Age'])
    db.session.add(new_person)
    db.session.commit()
    return jsonify({"message": "Personaje creado", "id": new_person.Id}), 201

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": f"Personaje con id {people_id} eliminado exitosamente"}), 200



@app.route('/planets', methods=['GET'])
def get_planets():
    planet_list = Planets.query.all()
    planet_JSON = [{'id': P.Id, 'Name': P.Name, 'Population': P.Population, 'Width': P.Width} for P in planet_list]
    return jsonify(planet_JSON), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    return jsonify({
        'id': planet.Id,
        'Name': planet.Name,
        'Population': planet.Population,
        'Width': planet.Width
    }), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data or 'Name' not in data or 'Population' not in data or 'Width' not in data:
        return jsonify({"error": "Faltan datos para crear un planeta"}), 400
    
    new_planet = Planets(Name=data['Name'], Population=data['Population'], Width=data['Width'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"message": "Planeta creado", "id": new_planet.Id}), 201

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": f"Planeta con id {planet_id} eliminado exitosamente"}), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_JSON = [{'id': user.id, 'email': user.email, 'is_active': user.is_active} for user in users]
    return jsonify(users_JSON), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Usuario fijo para este ejemplo
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_list = [{'id': fav.id, 'type': fav.type, 'item_id': fav.item_id} for fav in favorites]
    return jsonify({"favorites": favorite_list}), 200

# [POST] /favorite/planet/<int:planet_id> - Añadir un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Usuario fijo para este ejemplo
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    favorite = Favorite(user_id=user_id, type="planet", item_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": f"Planeta con id {planet_id} añadido a favoritos"}), 201

# [POST] /favorite/people/<int:people_id> - Añadir un personaje favorito
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = 1  
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    favorite = Favorite(user_id=user_id, type="people", item_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": f"Personaje con id {people_id} añadido a favoritos"}), 201

# [DELETE] /favorite/planet/<int:planet_id> - Eliminar un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  # Usuario fijo para este ejemplo
    favorite = Favorite.query.filter_by(user_id=user_id, type="planet", item_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "El favorito no existe"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": f"Planeta con id {planet_id} eliminado de favoritos"}), 200

# [DELETE] /favorite/people/<int:people_id> - Eliminar un personaje favorito
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = 1  # Usuario fijo para este ejemplo
    favorite = Favorite.query.filter_by(user_id=user_id, type="people", item_id=people_id).first()
    if not favorite:
        return jsonify({"error": "El favorito no existe"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": f"Personaje con id {people_id} eliminado de favoritos"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
