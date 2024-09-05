#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Relationships handled in the to_dict() methods
class Restaurants(Resource):
    def get(self):
        try:
            restaurants = Restaurant.query.all()
            return jsonify([restaurant.to_dict() for restaurant in restaurants])
        except Exception as e:
            app.logger.error(f"Error retrieving restaurants: {e}")
            return make_response(jsonify({"error": "An error occurred while retrieving restaurants"}), 500)

class RestaurantDetail(Resource):
    def get(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                response = restaurant.to_dict()
                response['restaurant_pizzas'] = [
                    rp.to_dict() for rp in RestaurantPizza.query.filter_by(restaurant_id=id).all()
                ]
                return jsonify(response)
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        except Exception as e:
            app.logger.error(f"Error retrieving restaurant with id {id}: {e}")
            return make_response(jsonify({"error": "An error occurred while retrieving the restaurant"}), 500)

    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                db.session.delete(restaurant)
                db.session.commit()
                return '', 204
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        except Exception as e:
            app.logger.error(f"Error deleting restaurant with id {id}: {e}")
            return make_response(jsonify({"error": "An error occurred while deleting the restaurant"}), 500)

class Pizzas(Resource):
    def get(self):
        try:
            pizzas = Pizza.query.all()
            return jsonify([pizza.to_dict() for pizza in pizzas])
        except Exception as e:
            app.logger.error(f"Error retrieving pizzas: {e}")
            return make_response(jsonify({"error": "An error occurred while retrieving pizzas"}), 500)

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            if data.get('price') < 1 or data.get('price') > 30:
                return make_response(jsonify({"errors": ["Price must be between 1 and 30"]}), 400)

            restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id')
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return jsonify(restaurant_pizza.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Error creating restaurant_pizza: {e}")
            return make_response(jsonify({"errors": ["An error occurred while creating the restaurant pizza"]}), 422)

# Add resources to API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
