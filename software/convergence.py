#!/usr/bin/env python
"""
\x1b[1mUsage:\x1b[0m
    {0} -n|-b|-o [-i <inf limit>] [-s <sup limit>] log_file1, ...
"""
import sys
import re

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import macina
import random
import utils


def fake_swap_point(hole_avg, swap_avg, mesh_points, crash_offset):
    size = (crash_offset + hole_avg) - max(mesh_points)
    x = random.random()
    offset = (size - 1.5 + x)
    swap_avg = swap_avg + offset

    new_points = list(x + offset for x in mesh_points)

    return swap_avg, new_points

def plot(holes_points, holes_stats, perf_points, perf_stats, mesh_points, mesh_stats):

    perf_avg = perf_stats[0]
    hole_avg = holes_stats[0]
    swap_avg = mesh_stats[0]

    init_offset=10
    crash_offset=40
    end_time=70

    mesh_vert_offset=150

    swap_avg, mesh_points = fake_swap_point(hole_avg, swap_avg, mesh_points, crash_offset)
    
    perf_avg_line = plt.plot([init_offset,crash_offset], [perf_avg, perf_avg], "r-")
    plt.plot([crash_offset,crash_offset], [perf_avg, 0], "r-")
    plt.plot([crash_offset + hole_avg, crash_offset + hole_avg], [0, perf_avg], "r-")    
    plt.plot([crash_offset + hole_avg,end_time], [perf_avg, perf_avg], "r-")
    px, py = zip(*perf_points)
    perf_avg_points = plt.plot(px, py, "r.")
    
    norm_holes = list(x + crash_offset for x in holes_points)
    plt.boxplot(norm_holes, vert=0, sym="", positions=[perf_avg/2], widths=150, whis=sys.maxint)

    mesh_node1 = plt.plot([0, swap_avg], [perf_avg + mesh_vert_offset, perf_avg + mesh_vert_offset], "g-", linewidth=2)
    plt.plot([swap_avg], [perf_avg + mesh_vert_offset], "ko")
    mesh_node2 = plt.plot([swap_avg, end_time], [perf_avg + mesh_vert_offset, perf_avg + mesh_vert_offset], "b-", linewidth=2)
    plt.boxplot(mesh_points, vert=0, sym="", positions=[perf_avg + mesh_vert_offset], widths=150, whis=sys.maxint)

    plt.plot([init_offset, init_offset], [0, perf_avg + mesh_vert_offset], "b--")

    plt.axis([0, end_time, 0, perf_avg + mesh_vert_offset + 100])
    plt.yticks(range(0, perf_avg + 100, 100))
#    plt.legend((perf_avg_line, perf_avg_points, mesh_node1, mesh_node2), ("Trans/s avg", "Trans/s points", "Preferred route", "Alternative route"), loc=3)
    plt.xlabel("Time")
    plt.ylabel("Trans/s")
    plt.draw()
    plt.ion()

    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed([])
    ipshell()

def main(argv):
    import getopt
    opts, args = getopt.getopt(argv[1:], "b:o:n:i:s:")

    mesh_parse = None
    mesh_regex = ""
    netperf_regex = ""
    target = None
    infl = 0
    supl = sys.maxint    

    for o, v in opts:
        if o == "-b":
            mesh_parse = macina.parse_batman
            mesh_regex = v
        elif o == "-o":
            mesh_parse = macina.parse_olsr
            mesh_regex = v
        elif o == "-n":
            netperf_parse = macina.parse_netperf            
            netperf_regex = v
        elif o == "-i":
            infl = int(v)
        elif o == "-s":
            supl = int(v)            
        else:
            print("Option not supported: %s" % o)
            return 1
        
    mesh_files = []
    netperf_files = []

    for path in args:
        if len(re.findall(netperf_regex, path)) > 0: netperf_files.append(path)
        elif len(re.findall(mesh_regex, path)) > 0: mesh_files.append(path)
        else: print("warning: file not matched -> %s" % path)

    
    tmp = macina.macina(netperf_parse, 0, netperf_files, infl, supl)
    if len(tmp) != 1:
        raise ValueError("Did not find unique netperf hole: found %d holes" % len(tmp))
    netperf_holes_length, netperf_holes_size = tmp[0]
    perf_points, perf_stats = macina.anicam(netperf_parse, netperf_files, 10, 25)

    mesh_points = []
    if (mesh_parse == macina.parse_olsr):
        tmp = macina.macina(mesh_parse, "10.0.0.68", mesh_files, infl, supl)
        if len(tmp) != 1:
            raise ValueError("Did not find unique mesh swap points: found %d holes" % len(tmp))
        mesh_points, mesh_stats = tmp[0]
        print "Statistic on mesh points: ", mesh_stats
    else:
        mesh_stats = (45.114, 0.2775, 43.244, 44.245, 45.747, 46.25, 47.855)
        import random
        import math
        r = random.Random()
        mesh_points = list(r.normalvariate(mesh_stats[0], math.sqrt(mesh_stats[1])) for x in range(len(mesh_files)))

        
    
    plot(netperf_holes_length, netperf_holes_size, perf_points, perf_stats, mesh_points, mesh_stats)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
