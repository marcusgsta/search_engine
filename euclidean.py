#!/usr/bin/python3
"""
Useful functions
"""
from sqlalchemy import create_engine
from json import dumps


db_connect = create_engine('sqlite:///movies.db')
# from User import User
# from Rating import Rating


def euclidean(userA, userB):
    """
    checks for similarity between users
    """
    # init variables
    sim = 0
    # Counter for number of matching products
    n = 0
    # Iterate over all rating combinations
    for rA in userA:
        for rB in userB:
            if rA[1] == rB[1]:
                sim += (rA[2] - rB[2])**2
                n += 1
    # No ratings in common - return 0
    if n == 0:
        return 0
    # Calculate inverted score
    inv = 1 / (1 + sim)
    return round(inv, 5)


# def getTopRated(user):
#     """
#     Get top rated movie from a user
#     """
#     userid = user[0]
#     conn = db_connect.connect()
#     query = conn.execute("select * from ratings where userid =%d " %int(userid))
#
#     ratings = {'ratings': [i for i in query.cursor.fetchall()]}
#
#     ratings['ratings'].sort(key = lambda x:x[2], reverse = True)
#
#     return ratings['ratings'][0]
