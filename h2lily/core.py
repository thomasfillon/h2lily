# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 09:23:42 2013

@author: thomas
TODO :
note group = tuple
group.add pour ajouter note à un group
group.time = la metrique
group = tuple de note, eventuellement singleton


REF : http://web.mit.edu/merolish/Public/drums.pdf
http://www.stevestreeting.com/2013/11/10/creating-drum-sheet-music-with-lilypond/
http://www.lilypond.org/doc/v2.19/Documentation/snippets/percussion
"""
from __future__ import division

from . lilypond import note_to_lily, REST

BEAT_LENGTH = 48
BEAT_PER_MEASURE = 4
MEASURE_LENGTH = BEAT_PER_MEASURE * BEAT_LENGTH

voices_config = [{'name': 'Up',
                  'instruments': [6, 12, 11]},  # Up
                 {'name': 'Down',
                  'instruments': [0, 2, 4]}]     # Down

# VOICES
UP = 1
DOWN = 2

"""
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
"""
#from math import *


class Voice_Config(object):
    def __init__(self, instruments=None, name=None, stem_direction=DOWN):
        if not instruments:
            instruments = []
        if not name:
            name = str(stem_direction)
        print 'name %s' % name
        self.name = name
        self.instruments = set(instruments)
        if stem_direction in [UP, DOWN]:
            self.stem_direction = stem_direction
        else:
            raise ValueError('Wrong value for voice stem_direction:' % stem_direction)


class Voices_Set(object):
    def __init__(self, voice=None):
        self._voices = {}
        self._next_up = 1
        self._next_down = 2

        if voice:
            self._add_voice(voice)

    @property
    def stem_up(self):
        return [voice for voice in self._voices
                if voice.stem_direction == UP]

    @property
    def stem_down(self):
        return [voice for voice in self._voices
                if voice.stem_direction == UP]

    def _add_voice(self, voice):
        # check instruments unicity
        for instru in voice.instruments:
            if instru in self.map_instrument:
                raise ValueError('Instrument %d already assigned' % instru)

        if voice.stem_direction == UP:
            self._voices[self._next_up] = voice
            self._next_up += 2
        elif voice.stem_direction == DOWN:
            self._voices[self._next_down] = voice
            self._next_down += 2
        else:
            raise ValueError('Bad value for stem_direction: %d' %
                             voice.stem_direction)

    @property
    def map_instrument(self):
        map_instru = {}
        for key, voice in self._voices.items():
            for instru in voice.instruments:
                map_instru[instru] = key
        print 'map_instru %s' % map_instru
        return map_instru

    def __len__(self):
        return len(self._voices)


class Pattern(dict):
    # Dict of
    def __init__(self, h2_pattern, voices=Voices_Set()):
        super(Pattern, self).__init__()
        self._voices = voices
        self.from_h2(h2_pattern)

    def _insert_note(self, measure, voice, position, instrument):
        print 'voice %s' % voice
        if not voice in self[measure]:
            self[measure][voice] = Voice()
            # Fill voice in measure with a rest
            empty_measure = Note(instrument=REST, duration=MEASURE_LENGTH)
            self[measure][voice][0] = empty_measure

        if not position in self[measure][voice]:
            previous_pos = max([k for k in self[measure][voice].keys()
                                if k < position])
            previous_note = self[measure][voice][previous_pos]
            duration = previous_note.duration - (position - previous_pos)
            previous_note.duration -= duration
            note = Note(instrument=instrument, duration=duration)
            self[measure][voice][position] = note
           # if a note start between two beats and end between two beats
            # then put a rest at the next beat after the note start
            next_beat_pos = (position + BEAT_LENGTH
                             - (position % BEAT_LENGTH))
            pos_is_beat = not(position % BEAT_LENGTH)
            dur_is_beats = not (duration % BEAT_LENGTH)
            end_position = position+duration

            if next_beat_pos <= MEASURE_LENGTH:
                if end_position > next_beat_pos:
                    if (not pos_is_beat and not dur_is_beats):
                        self._insert_note(measure, voice, next_beat_pos, REST)

        elif instrument != REST:
            if REST in self[measure][voice][position].instrument:
                # replace by instrument
                self[measure][voice][position].instrument = [instrument]

            else:
                # append instrument
                self[measure][voice][position].instrument.append(instrument)

    def from_h2(self, h2_pattern):

        self._name = h2_pattern.name
        self._size = h2_pattern.size

        # Initialize pattern with the proper number of measures
        if self._size % MEASURE_LENGTH:
            raise ValueError('Measure length does not fit pattern size')
        n_measures = self._size // MEASURE_LENGTH

        print "n_measures %d" % n_measures
        for measure in range(n_measures):
            self[measure] = Measure()
            self._insert_note(measure, voice=2, position=0, instrument=REST)

        map_instru = self._voices.map_instrument

        cnt = 0
        for note in h2_pattern.notes:
            pos = note.position % MEASURE_LENGTH
            measure = note.position // MEASURE_LENGTH

            instru = note.instrument
            voice = map_instru[instru]
            print "--- insert note ---"
            print "measure %s, voice %s , position %s, instrument %s" % (measure, voice, pos, instru)
            self._insert_note(measure=measure, voice=voice,
                              position=pos, instrument=instru)

    def fill_empty_measure(self):
        for measure, voices in self._dict:
            if not voices:
                #self[measure] = ...
                pass

    @property
    def lily_name(self):
        return 'patternA'  # self._name.replace(' ', '')

    def to_lily(self):
        measures_str_list = [self[measure].to_lily()
                             for measure in sorted(self)]
        measures_string = '\n'.join(measures_str_list)

        pattern_str = ("{name} = \drummode {{\n"
                       "{measures_string}\n"
                       "}}").format(name=self.lily_name,
                                    measures_string=measures_string)
        return pattern_str


class Measure(dict):
    """
    The stem directions are automatically assigned with the odd-numbered voices
    taking upward stems and the even-numbered voices downward ones.
    The stems for voices 1 and 2 are right, but the stems in voice 3 should
    go down in this particular piece of music. We can correct this by skipping
    voice three and placing the music in voice four.
    This is done by simply adding another pair of \\.
    """
    def to_lily(self):
        if not self.keys():
            return ""
        voice_max = max(self.keys())
        voices_string = ['    {}\n'.format(self.get(voice + 1,
                                                    Voice()).to_lily())
                         for voice in xrange(voice_max)]
        print '<<\n%s>>' % '    \\\\\n'.join(voices_string)
        return '<<\n%s>>' % '    \\\\\n'.join(voices_string)


class Voice(dict):
    def to_lily(self):
        notes_string = [self[position].to_lily() for position in sorted(self)]
        voice_str = ' '.join(notes_string)
        return '{{{}}}'.format(voice_str)


class Note(object):
    def __init__(self, instrument, duration):
        self.instrument = []
        if isinstance(instrument, list):
            self.instrument.extend(instrument)
        else:
            self.instrument.append(instrument)
        self.duration = duration

    def to_lily(self):
        return note_to_lily(self)
