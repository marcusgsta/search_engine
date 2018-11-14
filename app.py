#!/usr/bin/python3

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

from User import User
from Rating import Rating
from euclidean import euclidean

app = Flask(__name__)

# Make it easier to debug
app.debug = True
app.config.update(
    PROPAGATE_EXCEPTIONS=True
)



userA = User("Martin", 1)
userB = User("Sara", 2)
rA = Rating(1, "Me, You and Dupree", 2.5)

print euclidean(userA, userB)
