#!/usr/bin/env python

import re
from itertools import imap as map

MATCH_HOST = r'(\d+\.\d+\.\d+\.\d+)'
MATCH_HOST_SCORE = MATCH_HOST + r'\s*\(\s*(\d+)\)'

ROW_PATTERN = re.compile(r'^\s*%s\s+%s:\s*(.*)\s*$' % \
                         (MATCH_HOST, MATCH_HOST_SCORE))
TAIL_PATTERN = re.compile(r'^%s\s*(.*)$' % MATCH_HOST_SCORE)

class Host (object) :

    def __init__ (self, host, score=None):
        self.host = host
        self.score = score

    def __hash__ (self):
        return hash(self.host)

    def __cmp__ (self, x):
        return cmp(self.host, x.host)

    def __str__ (self):
        if self.score:
            return 'Host "%s" (%d)' % (self.host, self.score)
        return 'Host "%s"' % self.host

class TargetHost (Host) :

    def __init__ (self, host):
        super(TargetHost, self).__init__(host)
        self.gateway = None
        self.gwscore = 0
        self.alt = dict()

    def update (self, gw, alt):
        self.gateway = gw
        self.alt.update(((x.host, x) for x in alt))

    def quality_of (self, x):
        agw = self.alt.get(x)
        if not agw:
            return 0
        return agw.score or 0

class Status :

    class ParseError (Exception): pass

    def __init__ (self, stream):
        self.nodes = dict()
        self.stream = enumerate(map(lambda x : x.strip(), stream))
        nr, row = next(self.stream)
        if not Status.is_update(row):
            raise Status.ParseError('Invalid input file format')

    @staticmethod
    def parse_line (line):

        def parse_tail (tail):
            subm = re.match(TAIL_PATTERN, tail)
            while subm:
                ip, score, tail = subm.groups()
                yield Host(ip, int(score))
                subm = re.match(TAIL_PATTERN, tail)

        m = re.match(ROW_PATTERN, line)
        if m:
            dest, gateway, score, alt = m.groups()
            return dest, Host(gateway, int(score)), parse_tail(alt)

    @staticmethod
    def is_update (row):
        return row.startswith('\x1b[H\x1b[2J')

    def get_entry (self, hostname):
        ret = self.nodes.get(hostname)
        if not ret:
            ret = self.nodes[hostname] = TargetHost(hostname)
        return ret

    def step (self):
        eof = True
        for nr, row in self.stream:
            if Status.is_update(row):
                break
            dest, gw, alt = Status.parse_line(row)
            self.get_entry(dest).update(gw, alt)
            eof = False

        return not eof

    def __iter__ (self):
        return self.nodes.iteritems()

