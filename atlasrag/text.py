import re
import math
import hashlib
from collections import Counter

STOP = set("a an the is are was were be been to of in on at for and or with as by from this that it its how what which when where why can do does".split())

def tokens(text):
    return [x for x in re.findall(r"[a-z0-9]+", text.lower()) if x not in STOP]

def chunks(text, size=110, overlap=20):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")
    words = text.split()
    for start in range(0, len(words), size-overlap):
        part = words[start:start+size]
        if part:
            yield " ".join(part)
        if start+size >= len(words):
            break

def hashed_vector(text, dims=256):
    vec = [0.0]*dims
    for term, count in Counter(tokens(text)).items():
        digest = hashlib.sha256(term.encode()).digest()
        idx = int.from_bytes(digest[:4], "big") % dims
        sign = 1 if digest[4] % 2 == 0 else -1
        vec[idx] += sign*(1+math.log(count))
    norm = math.sqrt(sum(x*x for x in vec))
    return [v/norm for v in vec] if norm else vec

def cosine(a,b):
    return sum(x*y for x,y in zip(a,b))
