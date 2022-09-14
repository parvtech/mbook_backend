import binascii
import os
import random


def generate_token(self, *args, **kwargs):
    """generates a pseudo random code using os.urandom and binascii.hexlify"""
    # determine the length based on min_length and max_length
    length = random.randint(150, 256)

    # generate the token using os.urandom and hexlify
    return binascii.hexlify(os.urandom(256)).decode()[0:length]
