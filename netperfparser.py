#!/usr/bin/env python

import re
import sys
from itertools import islice, \
                      imap as map, \
                      izip_longest as izipl

FLOAT = '\\d+\\.\\d+'
RESULT = r'^Interim result: *({0}) +10\^(\d+)bits/s over ({0}) seconds'
PATTERN = re.compile(RESULT.format(FLOAT))

def NetperfParser (f):

    def parse_row (row):
        m = re.match(PATTERN, row)
        if m:
            speed, multip, interval = m.groups()
            return float(interval), float(speed) * (10 ** float(multip))
        return None

    for row in f:
        data = parse_row(row)
        if data: yield data

def Netperf2Gnuplot (*files):

    def parallelize ():
        parsed = map(NetperfParser, files)
        for fpars in izipl(*parsed):
            yield tuple(map(lambda x : x[1] if x else 0, fpars))

    def build_str (n, tup):
        yield '%d' % n
        for v in tup:
            yield str(v)

    for n, tup in enumerate(parallelize()):
        yield ' '.join(build_str(n, tup))

