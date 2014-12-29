# -*- coding: utf-8 -*-
"""
Created on Tue May  6 09:48:41 2014

@author: thomas
"""

from fractions import Fraction

REST = -1

mapNotes = {REST: 'r',  # Rest
            0: 'bd',
            2: 'sn',
            4: 'sn',
            6: 'hh',
            11: 'cb'}


def note_to_lily(note):
    # Instrument
    instruStr = lily_instrument(note.instrument)

    # Duration
    lilyStr = []
    for (prefix, duration) in lily_duration(note.duration):
        lilyStr.append('%s%s%s' % (prefix, instruStr, duration))
        instruStr = mapNotes[REST]

    return ' '.join(lilyStr)


def lily_instrument(h2_instru_list):
    if len(h2_instru_list) == 1:
        lily_instru = mapNotes[h2_instru_list[0]]
    else:
        lily_instru = '<%s>' % ' '.join(map(str,
                                            [mapNotes[instru]
                                                for instru in h2_instru_list]))
    return lily_instru


def lily_duration(duration):
    dur = duration
    frac = Fraction(dur, 192)
    note = [int(pow(2, n)) for n in xrange(0, 8)]
    ref_duration = [192//n for n in note]
    mask = []
    for d, n in zip(ref_duration, note):
        frac = Fraction(dur, d)
        # dot note
        if frac >= Fraction(3, 2) and d > 1 and d <= 96:
            mask.append(('', str(n)+'.'))
            dur -= Fraction(3*d, 2)
        elif frac >= 1:
            mask.append(('', str(n)))
            dur -= d
        # triplet (3-plet)
        elif frac == Fraction(2, 3):
            mask.append(('\\times 2/3 ', str(n)))
            dur -= Fraction(2*d, 3)
        # quintuplet (5-plet)
        elif frac == Fraction(4, 5):
            mask.append(('\\times 4/5 ', str(n)))
            dur -= Fraction(4*d, 5)

    if dur > 0:
        print mask
        print "duration : %d, \tremains :%f" % (duration, dur)

    return mask



def makeHeader(songTitle='H2 Drum score',
               songComposer='Hydrogen',
               tagline='Score generated with H2Lily, Copyright: Thomas Fillon, 2013',
               instrument='Drums'):

    header = ('\\version "2.14.2"\n'
    '\\header {{\n'
    '\ttitle = "{0}"\n'
    '\tcomposer = "{1}"\n'
    '\ttagline = "{2}"'
    '\tinstrument = "{3}"\n'
    '}}\n').format(songTitle, songComposer, tagline, instrument)
    return header



#
