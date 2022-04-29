import math, itertools
import hashlib
import settings

def trailing_zeros(n):
    # Number of trailing 0s in binary representation of integer n.#
    if n <= 0:
        return 0
    for i in itertools.count(0):
        if n & (1 << i):
            return i


def irange(n):
    # Implementation of xrange(n) that does not overflow.#
    i = 0
    while i < n:
        yield i
        i += 1


def all_strings(charset='0123456789ABCDEF'):
    # Yields all strings in given character set, sorted by length.#
    m = len(charset)
    for n in itertools.count(0):
        for i in irange(m ** n):
            yield ''.join([charset[(i // (m ** j)) % m] for j in range(n)])


def hash(s):
    # Hash function used by hashcash. Returns an integer.#
    sha = hashlib.sha256()
    sha.update(s)
    return int(sha.hexdigest(), 16)


def make_token(s, n, charset='0123456789ABCDEF'):
    # Makes hashcash token of value 'n' against basestring 's'.#
    s = s.encode(settings.FORMAT)
    sha = hashlib.sha256()
    sha.update(s)
    h = sha.digest()
    for token in all_strings(charset):
        token = token.encode(settings.FORMAT)
        if trailing_zeros(hash(h + token)) >= n: return token


def verify_token(s, token):
    # Returns hashcash value of given token against basestring 's'.#
    s = s.encode(settings.FORMAT)
    sha = hashlib.sha256()
    sha.update(s)
    # token = token.encode(settings.FORMAT)
    return trailing_zeros(hash(sha.digest() + token))


def make_cluster(s, n, charset='0123456789ABCDEF'):
    # Makes hashcash cluster of value 'n' against basestring 's'.#
    return '-'.join([make_token(s + str(i), n - 4, charset) for i in range(16)])


def verify_cluster(s, token):
    # Hashcash value of the given cluster against basestring 's'.#
    T = token.split('-')
    return min([verify_token(s + str(i), T[i]) for i in range(len(T))]) + \
           int(math.log(len(T)) / math.log(2.0))
