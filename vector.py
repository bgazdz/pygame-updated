import math


def dot_product(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dot_product(v, v))


def angle_between(v1, v2):
    return math.acos(dot_product(v1, v2) / (length(v1) * length(v2)))  # returns angle in radians


def multiply_scalar(v, scalar):
    return [i * scalar for i in v]


def distance(a, b):
    return math.sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]))