from RainbowTables import KeySpace, HashSearch

import ipywidgets as widgets
import hashlib
import random
import time
import re

# Terrible hash function
def shorty_hash(input):
    return hashlib.md5(input.encode('ascii')).hexdigest()[:6]

# A reduction function
def hash_to_key(hash_digest, salt, key_length, allowable_chars):
    hash_in_binary = str()

    for c in hash_digest:
        hash_in_binary += bin(ord(c))[2:].zfill(8)
        
    binary_chunks = int(len(hash_in_binary)/key_length)
    key_from_hash = str()
    for i in range(0, key_length):
        left_bound = i*binary_chunks
        right_bound = (i+1)*binary_chunks
        if i == (key_length-1):
            right_bound = len(hash_in_binary)
        list_pos = int(hash_in_binary[left_bound:right_bound], 2)%len(allowable_chars)
        key_from_hash += allowable_chars[list_pos]
        
    return key_from_hash

def key_gen(key_length, allowable_chars):
    key = str()
    for i in range(0, key_length):
        key += random.choice(allowable_chars)
    
    return key

def chain_gen(chain_length, key_length, allowable_chars):
    key = key_gen(key_length, allowable_chars)
    for i in range(0,chain_length):
        key_hash = shorty_hash(key)
        print(key, "=>", key_hash, "=> ", end='')
        key = hash_to_key(key_hash, 0, key_length, allowable_chars)
    print()
    

