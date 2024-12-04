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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def handle_hello():
    people_list = People.query.all()
    people_JSON = [{'id': P.Id, 'Name': P.Name, 'Last_Name': P.Last_Name, 'Age': P.Age} for P in people_list]

    return jsonify(people_JSON), 200


@app.route('/people', methods=['POST'])
def crear_usuario():
    try:

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        name = data.get('Name')
        last_name = data.get('Last_Name')
        age = data.get('Age')

        if not name or not last_name or not isinstance(age, int):
            return jsonify({"error": "Faltan datos o son inválidos"}), 400

        new_person = People(Name=name, Last_Name=last_name, Age=age)

        
        db.session.add(new_person)
        db.session.commit()

        
        return jsonify({
            "message": "Usuario creado exitosamente",
            "user": {
                "id": new_person.Id,
                "Name": new_person.Name,
                "Last_Name": new_person.Last_Name,
                "Age": new_person.Age
            }
        }), 201
    except Exception as e:
    
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500



@app.route('/planets', methods=['GET'])
def obtener_planetas():
    planet_list = Planets.query.all()
    planet_JSON = [{'id': P.id, 'Name': P.Name, 'Population': P.Population, 'Width': P.Width, } for P in planet_list]

    return jsonify(planet_JSON), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
