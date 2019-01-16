from random import random
from hashlib import md5

def gen_unique_str():
    '''
    Generate a unique string using the MD5 hash algo
    '''
    rand_str = str(random())
    hash_obj = md5()
    hash_obj.update(rand_str.encode('utf-8'))

    return hash_obj.hexdigest()
