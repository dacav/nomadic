#!/usr/bin/env python

import sys
import re
from itertools import imap as map, \
                      izip as zip

FLOAT = '\\d+\\.\\d+'
PATTERN = re.compile('^.*time=({0}).*$'.format(FLOAT))

def PingParser (f):
    for row in f:
        m = re.match(PATTERN, row)
        if m:
            yield float(m.groups()[0])

def Ping2Gnuplot (*files):

    def parallelize ():
        return zip(*map(PingParser, files))

    def build_str (n, tup):
        yield '%d' % n
        for v in tup:
            yield str(v)

    for n, tup in enumerate(parallelize()):
        yield ' '.join(build_str(n, tup))

