#!/usr/bin/env python

import re
import sys
from itertools import islice, \
                      imap as map, \
                      izip_longest as izipl

FLOAT = '\\d+\\.\\d+'
PATTERN = r'^Interim result: *({0}) +10\^(\d+)bits/s over ({0}) seconds'

def IperfParser (fn):

    pat = re.compile(PATTERN.format(FLOAT))
    def parse_row (row):
        m = re.match(pat, row)
        if m:
            speed, multip, interval = m.groups()
            return float(interval), float(speed) * (10 ** float(multip))
        return None

    try:
        f = open(fn, 'rt')
        for row in f:
            data = parse_row(row)
            if data: yield data
        f.close()
    except IOError, msg:
        print >>sys.stderr, "Warning: Skip %s: %s" % (fn, str(msg))

def Iperf2Gnuplot (*files):

    def parallelize ():
        parsed = map(IperfParser, files)
        for fpars in izipl(*parsed):
            yield tuple(map(lambda x : x[1] if x else 0, fpars))

    def build_str (n, tup):
        yield '%d' % n
        for v in tup:
            yield str(v)

    for n, tup in enumerate(parallelize()):
        yield ' '.join(build_str(n, tup))

