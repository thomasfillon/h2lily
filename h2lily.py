# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:23:42 2013

@author: thomas
"""

import xml.etree.ElementTree as ET
import numpy as np

beatLength = 48
mapVoice = [[6, 12, 11],  # Up
            [0, 2, 4]]  # Down

nbVoices = len(mapVoice)

mapNotes = {0: 'bd',
            2: 'sn',
            4: 'sn',
            6: 'hh',
            11: 'cb'}


mapDuration = {1: '128',
               3: '64',
               6: '32',
               9: '32.',
               12: '16',
               18: '16.',
               24: '8',
               36: '8.',
               48: '4',
               72: '4.',
               96: '2',
               144: '2.',
               192: '1'}

from fractions import *
from math import *


def find_duration(dur):

    note = np.power(2,range(0,8))
    duration = 192/note
    mask = []
    for d in duration:
        if dur >= d:
            mask.append(True)
            dur -= d
        else:
            mask.append(False)


    return [n for n,m in zip(note,mask) if m]

def find_fraction(duration):
    dur = duration
    frac = Fraction(dur,192)
    note = np.power(2, range(0,8))
    ref_duration = 192/note
    mask = []
    for d,n in zip(ref_duration, note):
        frac = Fraction(dur, d)
        # dot note
        if frac >= Fraction(3, 2) and d > 1:
            mask.append(('',str(n)+'.'))
            dur -= Fraction(3*d, 2)
        elif frac >= 1:
            mask.append(('',str(n)))
            dur -= d
        # triplet (3-plet)
        elif frac == Fraction(2,3):
            mask.append(('\\times 2/3 ',str(n)))
            dur -= Fraction(2*d,3)
        # quintuplet (5-plet)
        elif frac == Fraction(4,5):
            mask.append(('\\times 4/5 ',str(n)))
            dur -= Fraction(4*d,5)

    if dur >0:
        print mask
        print "duration : %d, \tremains :%f" % (duration,dur)

    return mask


def egypt(f):
    e=int(f)
    f-=e
    liste=[e]
    while(f.numerator>1):
        e=Fraction(1,int(ceil(1/f)))
        liste.append(e)
        f-=e
    liste.append(f)
    return liste


def readH2Pattern(pattern):
    size = int(pattern.find('size').text)
    nbbeats = size / beatLength  # TODO check pattern length

    noteListNode = pattern.find('noteList')

    noteList = []
    for note in noteListNode.iter('note'):
        instrument = int(note.find('instrument').text)
        position = int(note.find('position').text)
        #length = note.find('length')
        noteList.append((position, instrument))


    print "Instruments :"
    instruments = []
    for (pos, instru) in noteList:
        if instru not in instruments:
            instruments.append(instru)
            print  "%d" % instru
    #noteList = np.array(noteList)

    # Break up in voices
    notesVoice = []
    for voiceInstru in mapVoice:
        notesVoice.append([note for note in noteList if note[1] in voiceInstru])
    # TODO : print warning about instruments not in mapVoice

    # Break up in beats
    notesBeat = []
    for voice in notesVoice:
        beatList = []
        for n in range(nbbeats):
            beat = [(note[0]-n*beatLength, note[1]) for note in voice if note[0]>=n*beatLength and note[0]<(n+1)*beatLength]
            beat.sort()
            beatList.append(beat)
        notesBeat.append(beatList)

    # Group on position
    notesPosition = []
    for voice in notesBeat:
        beatList = []
        for beat in voice:
            position = []
            instruments = []
            if len(beat):
                position.append(beat[0][0])
                instruments.append([beat[0][1]])
                for note in beat[1:]:
                    try:
                        ind = position.index(note[0])
                        instruments[ind].append(note[1])
                    except:
                        position.append(note[0])
                        instruments.append([note[1]])
                beatList.append(zip(position, instruments))
        notesPosition.append(beatList)

    lilyMeasure = []
    for voice in notesPosition:
        lilyBeat = []
        for beat in voice:
            if len(beat) == 0:
                lilyBeat.append('r4')
            else:
                if beat[0][0] > 0:
                    for (prefix, duration) in find_fraction(beat[0][0]):
                        lilyBeat.append('%sr%s' % (prefix, duration))
                position = [note[0] for note in beat]
                position .append(beatLength)
                instrument = [note[1] for note in beat]

                def mapInstru(instrument):
                    if len(instrument) <= 1:
                        instruStr = mapNotes[instrument[0]]
                    else:
                        instruStr = '<%s>' % ' '.join(map(str,
                                  [mapNotes[instru] for instru in instrument]))
                    return instruStr
                instrumentStr = map(mapInstru, instrument)
                beatDiff = np.diff(position)

                str_list = []
                for n,instruStr in zip(beatDiff,instrumentStr):
                    for (prefix, duration) in find_fraction(n):
                        str_list.append('%s%s%s' % (prefix,instruStr,duration))


                lilyStr = ' '.join(str_list)
                print lilyStr

                lilyBeat.extend(str_list)
        lilyMeasure.append(lilyBeat)

    lilyDrumVoice = []
    for voice in lilyMeasure:
        lilyDrumVoice.append('    {%s}\n' % ' '.join(map(str, voice)))

    lilyDrumMeasureStr = '<<\n%s>>\n' % '    \\\\\n'.join(lilyDrumVoice)

    return lilyDrumMeasureStr

def makeHeader(songTitle = 'H2 Drum score',
               songComposer = 'Hydrogen',
               tagline = 'Score generated with H2Lily, Copyright: Thomas Fillon, 2013',
               instrument = 'Drums'):

    header = ('\\version "2.14.2"\n'
    '\\header {{\n'
    '\ttitle = "{0}"\n'
    '\tcomposer = "{1}"\n'
    '\ttagline = "{2}"'
    '\tinstrument = "{3}"\n'
    '}}\n').format(songTitle,songComposer,tagline,instrument)
    return header


def main():
    #h2File = "Pattern 1.h2pattern"
    h2File = "Pattern2.h2pattern"
    #h2File = "PatternOff.h2pattern"
    h2File  = "PatternTriple.h2pattern"

    tree = ET.parse(h2File)
    root = tree.getroot()

    pattern = root.find('pattern')

    patternStr = readH2Pattern(pattern)

    header = makeHeader()

    # Patterns definition
    patternName = 'patternA'
    PatternDefinition = ('%% -- Patterns definition --\n'
                         '%s = \\drummode {\n%s}\n') % (patternName, patternStr)

    drumScore = '%% -- Score --\ndrumScore = {\n\t\\%s\n}\n' % patternName

    drumStaff = """\\new DrumStaff <<
        \\tempo 4=102
        \\time 4/4
        \\set Timing.baseMoment = #(ly:make-moment 1 8)
        \\set Timing.beatStructure = #'(2 2 2 2)
        \\set Timing.beamExceptions = #'()
    """
    for i in range(nbVoices):
        drumStaff += '    \\new DrumVoice = "%d" { s1 *4 }\n' % i

    drumStaff += '    \\drumScore\n>>'

    lilyDoc = header + '\n' + PatternDefinition + '\n' + drumScore + '\n' + drumStaff
    fileName = h2File + '.ly'

    with open(fileName, 'w+') as lilyFile:
        lilyFile.write(lilyDoc)

if __name__ == "__main__":
    main()

