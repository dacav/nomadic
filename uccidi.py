#!/bin/env python

import netperfparser
import batparser
import olsrparser
import traceback
import sys
import macina


def parse_netperf(path):
    return list(netperfparser.NetperfParser(path, 10, netperfparser.BY_TRANSACTIONS))

def parse_batman(path):
    parser = batparser.BatParser(path, 70)
    return list(parser.iter_nexthop_ts("10.0.0.67"))

def parse_olsr(file):
    parser = olsrparser.OlsrParser(file)
    return parser.parse("10.0.0.67")

def uccidi(mesh_files, netperf_files, mesh_parse):
    mesh_files.sort()
    netperf_files.sort()

    for mesh_path, netp_path in zip(mesh_files, netperf_files):
        try:
            print("Processing %s - %s" % (mesh_path, netp_path))
            mesh_results = mesh_parse(mesh_path)
            netp_results = parse_netperf(netp_path)

            mcount = ncount = 0
            found = False
            for i in range(0, max(len(mesh_results), len(netp_results))):
                m = None
                n = None
                if len(mesh_results) > mcount:
                    m = mesh_results[mcount]

                if len(netp_results) > ncount:
                    n = netp_results[ncount]

                if n != None and not found and int(n[1]) == 0:
                    print("-----------------------------------------------")
                    found = True
                if n != None and found and int(n[1]) != 0:                    
                    print("-----------------------------------------------")
                    found = False
                    
                rm = int(round(m[0])) if m != None else sys.maxint
                rn = int(round(n[0])) if n != None else sys.maxint
                if rm == rn:
                    mcount += 1
                    ncount += 1
                    mstr = "(%.3f, %s)" % (m[0], m[1])
                    nstr = "(%.3f, %d)" % (n[0], n[1])
                elif rm < rn:
                    mcount += 1
                    mstr = "(%.3f, %s)" % (m[0], m[1])
                    nstr = "---"                    
                else:
                    ncount += 1
                    mstr = "---"
                    nstr = "(%.3f, %d)" % (n[0], n[1])                    
                print("%18s \t - \t %12s" % (mstr, nstr))                    
                    
        except Exception as e:
            print e
            traceback.print_exc()


def main(argv):
    import getopt
    import re
    
    opts, args = getopt.getopt(argv[1:], "b:o:n:")

    mesh_parse = None
    mesh_regex = ""
    netperf_regex = ""
    
    for o, v in opts:
        if o == "-b":
            mesh_parse = parse_batman
            mesh_regex = v
        elif o == "-o":
            mesh_parse = parse_olsr
            mesh_regex = v
        elif o == "-n":
            netperf_regex = v
        else:
            print("Option not supported: %s" % o)
            return 1

    
    mesh_files = []
    netperf_files = []

    for path in args:
        if len(re.findall(netperf_regex, path)) > 0: netperf_files.append(path)
        elif len(re.findall(mesh_regex, path)) > 0: mesh_files.append(path)
        else: print("warning: file not matched -> %s" % path)

    uccidi(mesh_files, netperf_files, mesh_parse)
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
