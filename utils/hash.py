"""
The Mozilla hash implementation can be found here:

https://searchfox.org/mozilla-central/source/toolkit/components/places/Helpers.cpp
https://searchfox.org/mozilla-central/source/mfbt/HashFunctions.h


This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this file,
you can obtain one at http://mozilla.org/MPL/2.0/.
"""

GOLDEN_RATIO = 0x9E3779B9


def rotate_left(value):
    return ((value << 5) | (value >> 27)) & 0xFFFFFFFF


def add_to_hash(hash_value, value):
    return (GOLDEN_RATIO * (rotate_left(hash_value) ^ ord(value))) & 0xFFFFFFFF


def hash_simple(s, l):
    hash_value = 0
    for i in range(l):
        hash_value = add_to_hash(hash_value, s[i])
    return hash_value & 0xFFFFFFFF


def hash_url(url):
    l = len(url)
    prefix = -1
    for i in range(l):
        if url[i] == ':':
            prefix = i
            break

    return (((hash_simple(url, prefix) & 0x0000FFFF) << 32) & 0xFFFFFFFFFFFFFFFF) + (
        hash_simple(url, l) & 0xFFFFFFFFFFFFFFFF
    )


def hash_function(*args) -> str:
    if len(args) < 1 or len(args) > 2:
        raise ValueError("hash_function requires 1 or 2 arguments")

    url = args[0]
    mode = args[1] if len(args) == 2 else None

    res = hash_url(url)
    if mode == "prefix_lo":
        res = (res & 0x0000FFFF) << 32
    elif mode == "prefix_hi":
        res = (res & 0x0000FFFF) << 32
        res += 0xFFFFFFFF

    return str(res)
