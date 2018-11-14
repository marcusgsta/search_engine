#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

db_connect = create_engine('sqlite:///movies.db')
app = Flask(__name__)
api = Api(app)


class Users(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select id, name from users") # This line performs query and returns json result
        # return {'users': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID
        return {'users': [i for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID


class Ratings(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from ratings")
        # result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        # return jsonify(result)
        return {'ratings': [i for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID


class Username(Resource):
    def get(self, userid):
        conn = db_connect.connect()
        query = conn.execute("select * from users where id =%d " %int(userid))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)


api.add_resource(Users, '/users') # Route_1
api.add_resource(Ratings, '/ratings') # Route_2
api.add_resource(Username, '/users/<userid>') # Route_3


if __name__ == '__main__':
     app.run()
