#!/usr/bin/env python

import re
import sys
import itertools

FLOAT = '\\d+\\.\\d+'
RESULT = r'^Interim result: *({0}) +10\^(\d+)bits/s over ({0}) seconds'
#RESULT = r'^Interim result:\s*({0})\s.*(\d+)bits/s over ({0}) seconds'
ITERIM_PATTERN = re.compile(RESULT.format(FLOAT))
THROUGHPUT_PATTERN = re.compile('^.*({0}).*$'.format(FLOAT))


class NetperfParser:

    def __init__ (self, fn):
        self.thr_total = 0
        self.f = open(fn)

    def __del__ (self):
        self.f.close()

    def parse_row (self, row):
        m = re.match(ITERIM_PATTERN, row)
        if m:
            speed, multip, interval = m.groups()
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
            print row, data
            if data:
                # Interval and speed is extracted from data
                for i, sp in self.intervals(*itertools.imap(float, data)):
                    interval_acc += i
                    yield (interval_acc, sp)
            elif 'Local /Remote' in row:
                raise StopIteration()
        self.thr_total = \
                float(re.match(THROUGHPUT_PATTERN, row).groups()[0])

