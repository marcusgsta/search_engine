#!/usr/bin/python3
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api
# from sqlalchemy import create_engine
from json import dumps
# import itertools as it

from clusters import *

# db_connect = create_engine('sqlite:///movies.db')
app = Flask(__name__, template_folder='templates')
api = Api(app)

def printkclust(kclust,labels):
    for cluster in kclust:
        for id in cluster:
            print(labels[id])
        print('   ')


class Kmeans(Resource):
    def get(self, iters):
        headers = {'Content-Type': 'text/html'}
        iters = int(iters)
        # read data file
        blognames,words,data = readfile('blogdata.txt')
        kclust = kcluster(data,k=10,nrOfIterations=iters)


        # print(blognames)
        # print(words)
        # printkclust(kclust,blognames)
        # drawdendrogram(kclust,blognames,jpeg='blogclust.jpg')


        return make_response(render_template('clust.html', kclust=kclust, blognames=blognames, iters=iters), 200, headers)

class Kmeans2(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        # read data file
        blognames,words,data = readfile('blogdata.txt')
        kclust = kcluster(data,k=10)

        return make_response(render_template('clust.html', kclust=kclust, blognames=blognames), 200, headers)

# api.add_resource(Kmeans, '/') # Route
api.add_resource(Kmeans, '/<iters>') # Route
api.add_resource(Kmeans2, '/') # Route
# api.add_resource(Kmeans, '/kmeans') # Route


if __name__ == '__main__':
     app.run()
