#!/usr/bin/env python

import re
import sys
import itertools

FLOAT = '\\d+\\.\\d+'

# Regex for netperf's throughput
THROUG = r'^Interim result: *({0}) +10\^(\d+)bits/s over ({0}) seconds'

# Regex for netperf's transactions
TRANS = r'^Interim result:\s*({0}) Trans/s over ({0}) seconds'

THROUGHPUT_PATTERN = re.compile('^.*({0}).*$'.format(FLOAT))

BY_THROUGHPUT, BY_TRANSACTIONS = xrange(2)

class NetperfParser:

    def __init__ (self, fn, interp=BY_THROUGHPUT):
        self.thr_total = 0
        self.f = open(fn)
        pat = THROUG if interp == BY_THROUGHPUT else TRANS
        self.iterrim_pat = re.compile(pat.format(FLOAT))

    def __del__ (self):
        self.f.close()

    def parse_row (self, row):
        m = re.match(self.iterrim_pat, row)
        if m:
            speed, interval = m.groups()
            return float(interval), float(speed) # * (10 ** int(multip))
        return None

    def intervals (self, interval, speed):
        nsteps = int(round(interval))
        step = interval / nsteps
        speed /= nsteps
        for st in xrange(nsteps):
            yield (step, speed)

    def __iter__ (self):
        interval_acc = 0
        for row in self.f:
            data = self.parse_row(row)
            if data:
                # Interval and speed is extracted from data
                for i, sp in self.intervals(*data):
                    interval_acc += i
                    yield (interval_acc, sp)
            elif 'Local /Remote' in row:
                raise StopIteration()
        self.thr_total = \
                float(re.match(THROUGHPUT_PATTERN, row).groups()[0])

