#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantResource(Resource):
    def get(self, id=None):
        if id is not None:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                return {
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'address': restaurant.address,
                    'restaurant_pizzas': [rp.to_dict() for rp in restaurant.restaurant_pizzas]
                }, 200
            else:
                return {"error": "Restaurant not found"}, 404
        else:
            restaurants = Restaurant.query.all()
            return [{'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address} for restaurant in restaurants], 200
        
    def post(self):
        data = request.get_json()
        new_restaurant = Restaurant(name=data.get('name'), address=data.get('address'))
        db.session.add(new_restaurant)
        db.session.commit()
        return new_restaurant.to_dict(), 201

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzaResource(Resource):
    def get(self, id=None):
        if id:
            pizza = db.session.get(Pizza, id)
            if pizza:
                return pizza.to_dict(), 200
            else:
                return {"error": "Pizza not found"}, 404
        else:
            pizzas = Pizza.query.all()
            return [{'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients} for pizza in pizzas], 200

    def post(self):
        data = request.get_json()
        new_pizza = Pizza(name=data.get('name'), ingredients=data.get('ingredients'))
        db.session.add(new_pizza)
        db.session.commit()
        return new_pizza.to_dict(), 201

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')

        if not (1 <= price <= 30):
            return {'errors': ['validation errors']}, 400
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                restaurant_id=data.get('restaurant_id'),
                pizza_id=data.get('pizza_id')
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400

    def delete(self, id):
        restaurant_pizza = db.session.get(RestaurantPizza, id)
        if not restaurant_pizza:
            return {"error": "RestaurantPizza not found"}, 404
        db.session.delete(restaurant_pizza)
        db.session.commit()
        return {'message': 'RestaurantPizza deleted successfully'}, 200

api.add_resource(RestaurantResource, '/restaurants', '/restaurants/<int:id>')
api.add_resource(PizzaResource, '/pizzas', '/pizzas/<int:id>')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas', '/restaurant_pizzas/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)