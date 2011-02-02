#!/usr/bin/env python

'''
\x1b[1mUsage:\x1b[0m
    {0} -n|-b|-o [-i <inf limit>] [-s <sup limit>] log_file1, ...
'''

import sys
import netperfparser
import olsrparser
import batparser
import utils

def extract_point(data, target):
    prev_target = None
    plst = []
    
    for t, v in data:
        if prev_target == None:
            prev_target = v == target
            continue

        if prev_target and v != target:
            #Found change point
            plst.append(t)
            prev_target = False
        elif not prev_target and v == target:
            #Found change point
            plst.append(t)
            prev_target = True
            
    return plst

def parse_netperf(file):
    return list(netperfparser.NetperfParser(file, 10, netperfparser.BY_TRANSACTIONS))

def parse_batman(file):
    parser = batparser.BatParser(file, 70)
    return list(parser.iter_nexthop_ts("10.0.0.67"))

def parse_olsr(file):
    parser = batparser.BatParser(file, 70)
    return parser.iter_nexthop_ts("10.0.0.67")

def macina(parse, target, filelst, infl, supl):
    pointsdict = {}
    for path in filelst:
        data = parse(path)
        points = extract_point(data, target)
        points = filter(lambda x: x > infl, points)
        print path, points
        for i, p in enumerate(points):
            l = pointsdict.get(i, [])
            l.append(p)
            pointsdict[i] = l

    stats = []
    for points in pointsdict.itervalues():
        points = points
        avg = utils.average(points)
        var = utils.variance(points)
        q1, median, q3 = utils.quartiles(points)
        min(points)
        stats.append((avg, var, min(points), q1, median, q3, max(points)))
    return stats


def main():
    opts, args = getopt.getopt(sys.argv[1:], "nboi:s:")

    parse = None
    target = None
    infl = 0
    supl = sys.maxint

    for o,v in opts:
        if o == "-n":
            parse = parse_netperf
            target = 0
        if o == "-b":
            parse = parse_batman
            target = "10.0.0.67"
        if o == "-o":
            parse = parse_olsr
            target = "10.0.0.67"
        if o == "-i":
            infl = int(v)
        if o == "-s":
            supl = int(v)

    if parse == None:
        print "Specify a parsing mode"
        print __doc__.format(sys.argv[0])
        return 1

    if len(args) < 2:
        print "Specify at least 2 log files"
        print __doc__.format(sys.argv[0])
        return 1

    stats = macina(parse, target, args, infl, supl)
    for avg, var, minv, q1, median, q3, maxv in stats:
        print("avg=%.3f, var=%.3f, minv=%.3f q1=%.3f, median=%.3f, " \
              "q3=%.3f maxv=%.3f" % (avg, var, minv, q1, median, q3, maxv)) 

    return 0
    
if __name__ == "__main__":
    import getopt
    import sys

    sys.exit(main())

