#!/usr/bin/env python

import re
import sys
import itertools
import warnings

FLOAT = '\\d+\\.\\d+'

# Regex for netperf's throughput
THROUG = r'^Interim result: *({0}) .*bits/s over ({0}) seconds'

# Regex for netperf's transactions
TRANS = r'^Interim result:\s*({0}) Trans/s over ({0}) seconds'

# Regex for timing
TIMING = r'^.*({0}) seconds$'

THROUGHPUT_PATTERN = re.compile('^.* +({0}) *$'.format(FLOAT))
TIMING_PATTERN = re.compile(TIMING.format(FLOAT))

BY_THROUGHPUT, BY_TRANSACTIONS = xrange(2)

class NetperfParser:

    def __init__ (self, fn, time_offset=0, interp=BY_THROUGHPUT):
        self.thr_total = 0
        self.f = open(fn)
        self.filename = fn
        if interp == BY_THROUGHPUT:
            pat = THROUG
            self.intervals = self.thoughput_intervals
        elif interp == BY_TRANSACTIONS:
            pat = TRANS
            self.intervals = self.transaction_intervals
        else:
            raise SystemExit('You are kidding me, right?')

        pat = THROUG if interp == BY_THROUGHPUT else TRANS
        self.iterrim_pat = re.compile(pat.format(FLOAT))
        self.time_offset = time_offset

    def __del__ (self):
        self.f.close()

    def parse_row (self, row):
        m = re.match(self.iterrim_pat, row)
        if m:
            speed, interval = m.groups()
            return float(interval), float(speed) # * (10 ** int(multip))
        return None

    def thoughput_intervals (self, interval, speed):
        nsteps = int(round(interval))
        step = interval / nsteps
        speed /= nsteps
        for st in xrange(nsteps):
            yield (step, speed)

    def transaction_intervals (self, interval, trans):
        nsteps = int(round(interval))
        if nsteps == 1:
            yield interval, trans
        else:
            step = interval / nsteps
            for st in xrange(1, nsteps):
                yield (step, 0)
            yield (interval - (step * (nsteps - 1)), trans)

    def __iter__ (self):
        interval_acc = self.time_offset
        for nr, row in enumerate(self.f, 1):
            data = self.parse_row(row)
            if data:
                # Interval and speed is extracted from data
                for i, sp in self.intervals(*data):
                    interval_acc += i
                    yield (interval_acc, sp)
            elif 'Local /Remote' in row:
                # What? this works only with transactions!
                # Not that I care
                raise StopIteration()
            # else:
            #     warnings.warn('Skipping row {0} of file {1}'
            #                   .format(nr, self.filename))

        self.thr_total = \
                float(re.match(THROUGHPUT_PATTERN, row).groups()[0])

    def get_throughput (self):
        for row in self.f: pass
        return float(re.match(THROUGHPUT_PATTERN, row).groups()[0])

    def iter_timing (self):
        for row in self.f:
            try:
                yield re.match(TIMING_PATTERN, row).group(1)
            except:
                pass

def throughput_of (fn):
    ret = NetperfParser(fn).get_throughput()
    return ret
