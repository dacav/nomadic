#!/usr/bin/env python

import re
import sys
import itertools

FLOAT = '\\d+\\.\\d+'
RESULT = r'^Interim result: *({0}) +10\^(\d+)bits/s over ({0}) seconds'
ITERIM_PATTERN = re.compile(RESULT.format(FLOAT))
THROUGHPUT_PATTERN = re.compile('^.*({0}).*$'.format(FLOAT))

class NetperfParser:

    def __init__ (self, f):
        self.thr_total = 0
        self.f = f

    def parse_row (self, row):
        m = re.match(ITERIM_PATTERN, row)
        if m:
            speed, multip, interval = m.groups()
            return float(interval), float(speed) # * (10 ** int(multip))
        return None

    def split_interval (self, interval, speed):
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
                for i, sp in self.split_interval(*itertools.imap(float, data)):
                    interval_acc += i
                    yield (interval_acc, sp)
        try:
            self.thr_total = float(re.match(THROUGHPUT_PATTERN, row).groups()[0])
        except AttributeError, msg:
            sys.stderr.write(row)
            sys.stderr.write('\n')
            raise AttributeError(msg)

