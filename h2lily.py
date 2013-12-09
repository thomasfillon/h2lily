# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:23:42 2013

@author: thomas
TODO :
note group = tuple
group.add pour ajouter note à un group
group.time = la metrique
group = tuple de note, eventuellement singleton

"""
from __future__ import division

import xml.etree.ElementTree as ET

BEAT_LENGTH = 48
REST = -1

mapVoice = [[6, 12, 11],  # Up
            [0, 2, 4]]  # Down

nbVoices = len(mapVoice)

mapNotes = {REST: 'r',  # Rest
            0: 'bd',
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

from fractions import Fraction
#from math import *


def find_fraction(duration):
    dur = duration
    frac = Fraction(dur, 192)
    note = [int(pow(2, n)) for n in xrange(0, 8)]
    ref_duration = [192//n for n in note]
    mask = []
    for d, n in zip(ref_duration, note):
        frac = Fraction(dur, d)
        # dot note
        if frac >= Fraction(3, 2) and d > 1:
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

    if dur >0:
        print mask
        print "duration : %d, \tremains :%f" % (duration,dur)

    return mask



def h2read(h2file):

    import os.path
    extension = os.path.splitext(h2file)[1]

    tree = ET.parse(h2file)
    root = tree.getroot()

    if extension == '.h2pattern':
        xml_pattern = root.find('pattern')
        patternStr = h2Pattern(xml_pattern).lilyDrumMeasureStr

    return patternStr


class Note(object):
    def __init__(self, instrument=REST, position=0, duration=BEAT_LENGTH):
        self.instrument = []
        if instrument is not None:
            self.instrument.append(instrument)
        self.position = position
        self.duration = duration
        if self.duration > BEAT_LENGTH - self.position:
            raise ValueError('Duration exceed BEAT_LENGTH')

    def to_lily_string(self):
        # Instrument
        if len(self.instrument) == 1:
            instruStr = mapNotes[self.instrument[0]]
        else:
            instruStr = '<%s>' % ' '.join(map(str,
                          [mapNotes[instru] for instru in self.instrument]))

        # Duration
        lilyStr = []
        for (prefix, duration) in find_fraction(self.duration):
            lilyStr.append('%s%s%s' % (prefix, instruStr, duration))
            instruStr = mapNotes[REST]

        return lilyStr


class h2Pattern(object):
    def __init__(self, xml_pattern):
        self.nb_beats = None
        self.size = None
        self.name = None
        self.readH2Pattern(xml_pattern)

    def add_note(self, note):

        try:
            voice = [(note.instrument in voiceInstru)
                 for voiceInstru in mapVoice].index(True)
        except ValueError:
            raise ValueError('Instrument not in mapVoice')

        if note.instrument not in mapNotes:
            raise ValueError('Instrument not in mapNotes')

        beat = note.position // BEAT_LENGTH
        beat_position = note.position - beat * BEAT_LENGTH

        if self.pattern[voice][beat][-1].position == beat_position:
            if beat_position == 0 and REST in self.pattern[voice][beat][-1].instrument:
                self.pattern[voice][beat][-1].instrument.remove(REST)

            self.pattern[voice][beat][-1].instrument.append(note.instrument)

        else:
            note_duration = BEAT_LENGTH - beat_position

            self.pattern[voice][beat][-1].duration -= note_duration
            self.pattern[voice][beat].append(Note(position=beat_position,
                                                  instrument=note.instrument,
                                                  duration=note_duration))
        # Check duration
        dur = 0
        for note in self.pattern[voice][beat]:
            dur += note.duration
        if not dur == BEAT_LENGTH:
            raise ValueError

    def readH2Pattern(self, xml_pattern):
        """
        Read a Hydrogen pattern
        """

        self.size = int(xml_pattern.find('size').text)
        self.nb_beats = self.size // BEAT_LENGTH  # TODO check pattern length

        # Initialize pattern
        self.pattern = []
        for voice in range(len(mapVoice)):
            self.pattern.append([[Note()] for beat in range(self.nb_beats)])

        try:
            self.name = xml_pattern.find('pattern_name').text
        except AttributeError:
            self.name = xml_pattern.find('name').text

        noteListNode = xml_pattern.find('noteList')

        noteList = []
        from collections import namedtuple
        xml_note = namedtuple('Note', ['position', 'instrument'])
        for note in noteListNode.iter('note'):
            #length = note.find('length')
            noteList.append(xml_note(int(note.find('position').text),
                                     int(note.find('instrument').text)))

        noteList.sort()
        for note in noteList:
            self.add_note(note)  # Add note to self.pattern

        #print "Instruments :"
        self.instruments = set([note.instrument for note in noteList])
        #print self.instruments

        lilyMeasure = []
        for voice in self.pattern:
            lilyBeat = []
            for beat in voice:
                for note in beat:
                    lilyBeat.extend(note.to_lily_string())
            lilyMeasure.append(lilyBeat)

        lilyDrumVoice = []
        for voice in lilyMeasure:
            lilyDrumVoice.append('    {%s}\n' % ' '.join(map(str, voice)))

        lilyDrumMeasureStr = '<<\n%s>>\n' % '    \\\\\n'.join(lilyDrumVoice)
        self.lilyDrumMeasureStr = lilyDrumMeasureStr

        return self


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


def main():
    #h2file = "Pattern 1.h2pattern"
    h2file = "Pattern2.h2pattern"
    #h2file = "PatternOff.h2pattern"
    #h2file = "PatternTriple.h2pattern"

    patternStr = h2read(h2file)

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
    fileName = h2file + '.ly'

    with open(fileName, 'w+') as lilyFile:
        lilyFile.write(lilyDoc)

    import subprocess

    command = ['lilypond']
    command.append(h2file + '.ly')
    stdout = subprocess.check_output(command)


if __name__ == "__main__":
    main()
