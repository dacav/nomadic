#!/usr/bin/env python

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

