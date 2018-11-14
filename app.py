#!/usr/bin/python3

from User import User
from Rating import Rating
from euclidean import euclidean

userA = User("Martin", 1)
userB = User("Sara", 2)
rA = Rating(1, "Me, You and Dupree", 2.5)

print euclidean(userA, userB)
