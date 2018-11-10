"""
Rockstat calltracking library
(c) Dmitry Rodin 2018
"""
from random import randrange
from time import time


def pairs(l):
    """
    Convert list to pairs
    """
    for i in range(0, len(l), 2):
        # Create an index range for l of n items:
        yield (*l[i:i+2],)


def dictlist(dict_):
    """
    Convert dict to flat list
    """
    return [item for pair in dict_.items() for item in pair]


def gen_key(uid, section='s'):
    """
    Generate store key for own user
    """
    return f'ct:{section}:{uid}'.encode()


def rand_item(list_):
    if len(list_):
        return list_[randrange(0, len(list_))]


def ms():
    return int(time() * 1000)
