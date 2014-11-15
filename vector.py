import math


def dot_product(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dot_product(v, v))


def angle_between(v1, v2):
    return math.acos(dot_product(v1, v2) / (length(v1) * length(v2))) # returns angle in radians