#!/usr/bin/env python

import os.path
import itertools

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

    if len(seq) == 1: return seq[0], seq[0], seq[0]

    seq.sort()

    m0 = len(seq) / 2
    if len(seq) % 2:
        return aux(seq[:m0]), seq[m0], aux(seq[m0 + 1:])
    else:
        return aux(seq[:m0 - 1]), seq[m0 - 1], aux(seq[m0:])

class CmdLnError (Exception) : pass

def cmdline_parse (argv):

    import warnings

    def subplot_args (subls, items):
        subls = subls.split(',')
        i = 0
        for ls, fn in itertools.izip(subls, items):
            if (':' in fn) or (',' in fn):
                warning.warn('Weird filename: "%s"' % fn)
            yield ls, fn
            i += 1
        if i != len(subls):
            raise CmdLnError('Not all files have been provided')

    argv = iter(argv)
    try:
        for chunk in argv:
            params = chunk.split(':')
            if len(params) == 3:
                label, thrs, spec = chunk.split(':')
            else:
                label, spec = chunk.split(':')
                thrs = 0
            yield label, float(thrs), list(subplot_args(spec, argv))
    except:
        raise CmdLnError('Something wrong with params')

def cut_outlayers (data, factor=1, key=None):
    if factor == 0:
        return data
    if key != None:
        data = list(itertools.map(key, data))
    elif type(data) != list:
        data = list(data)
    avg = average(data)
    threshold = variance(data, avg) * factor
    return itertools.ifilter(lambda x : abs(x - avg) < threshold,
                             data)

