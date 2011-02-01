#!/usr/bin/env python

import os.path

def suggest (outstream, gnuplot_filename, xcol, *columns):
    '''
    Print 'suggested' gnuplot command.

    Parameter list:
        - outstream:    where to print command (typically stdout);
        - gnuplot_file: name of the file containing gnuplot data;
        - xcol:         column of counter (set it to Null in order not to
                        have one);
        - columns:      specification for data location (couples are
                        expected, in the (title, index) format, like
                        ('latency', 3) for instance).
    '''

    def suggest_list ():
        xidx = ('%d:' % xcol) if xcol != None else ''
        for title, idx in columns:
            yield '\'%s\' using %s%d w l title \'%s\'' % \
                  (gnuplot_filename, xidx, idx, title)

    outstream.write('plot ')
    outstream.write(','.join(suggest_list()))
    outstream.write('\n')

def safe_open (filename):
    if os.path.exists(filename):
        raise IOError('"%s" exists. Cowardly refusing to overwrite it' \
                      % filename)
    return open(filename, 'wt')

def average (seq):
    return sum(seq, 0.0) / len(seq)

def variance (seq, avg=None):
    if avg == None:
        avg = average(seq)
    return average(list((x - avg)**2 for x in seq))

def quartiles (seq):

    def aux (sub):
        half = len(sub) / 2
        if len(sub) % 2:
            return sub[half]
        else:
            return float(sub[half - 1] + sub[half]) / 2

    seq.sort()
    m0 = len(seq) / 2
    if len(seq) % 2:
        return aux(seq[:m0]), seq[m0], aux(seq[m0 + 1:])
    else:
        return aux(seq[:m0 - 1]), seq[m0 - 1], aux(seq[m0:])
