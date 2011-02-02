#!/usr/bin/env python

import re
from itertools import imap as map, izip as zip

MATCH_HOST = r'(\d+\.\d+\.\d+\.\d+)'
MATCH_SCORE = r'\(\s*(\d+)\)'

ROW_PATTERN = re.compile(r'%s\s+%s\s+%s.*$' % \
                         (MATCH_HOST, MATCH_SCORE, MATCH_HOST))
TIMESTAMP_PATTERN = re.compile(r'\s+Origi.*UT: \d+d\s+\d+h\s+(\d+)m.*$')

def parse_line (line):
    m = re.match(ROW_PATTERN, line)
    if m:
        dest, score, gateway = m.groups()
        return dest, gateway, int(score)
    return None

def data_begin (row): return 'BOD' in row
def file_end (row): return row.startswith('Interface activated:')

class BatParser :

    class ParseError (Exception): pass

    def __init__ (self, filename, exec_time):
        self.filename = filename
        self.file = open(filename)
        self.exec_time = int(exec_time)
        self.stream = enumerate(map(lambda x : x.strip(), self.file))

    def __del__ (self):
        self.file.close()

    def timestamps (self):
        fs = open(self.filename)

        def build_minute ():
            cur_min = 0
            steps_per_min = 0
            for nr, row in enumerate(fs):
                m = re.match(TIMESTAMP_PATTERN, row)
                if not m: continue
                minute = int(m.groups()[0])
                if minute > cur_min:
                    cur_min = minute
                    yield steps_per_min
                    steps_per_min = 0
                else:
                    steps_per_min += 1
            yield steps_per_min

        nmins = self.exec_time / 60
        crumbs = self.exec_time % 60

        # First instant (in which we shouldn't have a route yet)
        yield 0

        acc = 0
        for m, steps in enumerate(build_minute()):
            minlen = float(60 if m < nmins else crumbs)
            for i in xrange(1, steps + 1):
                yield acc + i * minlen / steps
            acc += minlen

        fs.close()

    def get_entry (self, hostname):
        ret = self.nodes.get(hostname)
        if not ret:
            ret = self.nodes[hostname] = TargetHost(hostname)
        return ret

    def iter_nexthop (self, target):
        # First line of each step (if any)
        try:
            nr, row = next(self.stream)
            if file_end(row):
                raise StopIteration()
            elif not data_begin(row):
                raise Status.ParseError('%s not starting on BOD (line %d)' \
                                        % (self.filename, nr))
        except StopIteration:
            raise Status.ParseError('%s broken starting step (line %d)' \
                                    % (self.filename, nr))

        # First instant (in which we shouldn't have a route yet)
        yield 'none' #, 0
        for nr, row in self.stream:
            data = parse_line(row)
            if not data:
                continue
            dest, gw, score = data
            if dest == target:
                yield gw #, score

    def iter_nexthop_ts (self, target):
        return zip(self.timestamps(), self.iter_nexthop(target))

