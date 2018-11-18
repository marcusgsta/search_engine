#!/usr/bin/python3
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from euclidean import *
import itertools as it

db_connect = create_engine('sqlite:///movies.db')
app = Flask(__name__, template_folder='templates')
api = Api(app)




class Users(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        conn = db_connect.connect() # connect to database
        query = conn.execute("select id, name from users")
        usernames = {'users': [i for i in query.cursor.fetchall()]}
        query2 = conn.execute("select * from users")
        users = [i for i in query2.cursor.fetchall()]
        return make_response(render_template('index.html', usernames=usernames, users=users),200,headers)



class Ratings(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        conn = db_connect.connect()
        query = conn.execute("select * from ratings")

        ratings = {'ratings': [i for i in query.cursor.fetchall()]}
        # get all users
        query5 = conn.execute("select * from users")
        users = [i for i in query5.cursor.fetchall()]
        return make_response(render_template('ratings.html', users=users, ratings=ratings), 200, headers)


class Username(Resource):
    def get(self, userid):
        USERID = userid
        headers = {'Content-Type': 'text/html'}
        conn = db_connect.connect()

        # Database calls
        #userA
        query = conn.execute("select * from ratings where userid =%d " %int(userid))
        userA = [i for i in query.cursor.fetchall()]
        # all ratings
        query4 = conn.execute("select * from ratings")
        ratings = [i for i in query4.cursor.fetchall()]
        # get all users
        query5 = conn.execute("select * from users")
        users = [i for i in query5.cursor.fetchall()]
        # username
        query3 = conn.execute("select * from users where id =%d " %int(userid))
        username = {'data': [dict(zip(tuple(query3.keys()), i)) for i in query3.cursor]}

        # create array
        similarities = []
        n = 0
        for user in users:
            query6 = conn.execute("select * from ratings where userid=%d " %int(user[0]))
            userX = [i for i in query6.cursor.fetchall()]

            if (user[0] != username['data'][0]['id']):
                similarities.append([user, euclidean(userA, userX)])

        print(similarities)
        def getSimScore(userid, sims):
            if userid < len(sims):
                return sims[userid][1]
            else:
                return 0

        ratingsWithWS = []
        # get weighted score (ws)
        # loop through ratings, check for each rating that user has given, and multiply by her similarity
        for rating in ratings:
            totalws = 0
            userid = rating[0] - 1
            ws = 0
            # get similarity for user
            simscore = getSimScore(userid, similarities)
            ws = rating[2] * simscore
            print("Current user:")
            print(userid+1)
            print("Current movie:")
            print(rating[1])
            print("Rated:")
            print(rating[2])
            print("Users simscore:")
            print(simscore)
            print("Weighted score:")
            print(str(ws))

            ratingsWithWS.append({
            'userid': userid+1,
            'movie': rating[1],
            'rating': rating[2],
            'similarity': simscore,
            'ws': ws
            })

        similarities = similarities[:3]
        print("ratings with WS")
        # sort ratingsWithWS on film instead of userids
        newratings = sorted(ratingsWithWS, key=lambda k: k['movie'])

        # sum total ws for each movie, group:
        def get_ws(movie):
            return lambda x: x['ws'] if x['movie']==movie else 0

        def get_sim(movie):
            return lambda x: x['similarity'] if x['movie']==movie else 0

        # get sum of similarity for all users with matching movies

        movies = sorted(set(map(lambda x: x['movie'], newratings)))
        result = [{'movie':movie, 'sumsim': sum(map(get_sim(movie), newratings)), 'sumws':sum(map(get_ws(movie), newratings))} for movie in movies]


        def getTotalDividedBySumsim(movie):
            return lambda x: x['sumws']/x['sumsim'] if x['movie']==movie else 0
        # calculate total ws divided by sum of similarity
        # for every movie
        newmovies = sorted(set(map(lambda x: x['movie'], result)))
        newresult = [{'movie':movie, 'divbysim': round(sum(map(getTotalDividedBySumsim(movie), result)),4)} for movie in newmovies]

        print(newresult)

        # exclude movies already seen by user
        def getAlreadySeen(userid):
            print(userid)
            #loop through ratings
            movies = []
            for rating in ratings:
                print("rating[0]")
                print(rating[0])
                userid = int(userid)
                if rating[0] == userid and any(d['movie'] == rating[1] for d in newresult):
                    print(rating[1])
                    movies.append(rating[1])
            return movies

        alreadySeen = getAlreadySeen(USERID)
        newresult[:] = [d for d in newresult if d.get('movie') not in alreadySeen]

        newresult.sort(key = lambda x:x['divbysim'], reverse = True)
        print(newresult)

        print("alreadySeen")
        print(alreadySeen)

        recommended_movies = newresult[:3]

        return make_response(render_template('username.html',users=users, username=username, similarities=similarities, ratingsWithWS=newratings, recommended_movies=recommended_movies), 200, headers)


api.add_resource(Users, '/') # Route_1
api.add_resource(Ratings, '/ratings') # Route_2
api.add_resource(Username, '/users/<userid>') # Route_3


if __name__ == '__main__':
     app.run()
