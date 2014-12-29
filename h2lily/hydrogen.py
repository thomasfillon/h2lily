# -*- coding: utf-8 -*-
"""
Created on Tue May  6 09:39:05 2014

@author: thomas
"""

from . import utils

import os.path
import xml.etree.ElementTree as ET

from collections import namedtuple


def h2pattern_read(h2file):
    """Read an Hydrogen pattern file (with extension '.h2pattern')"""
    #  Check extension
    extension = os.path.splitext(h2file)[1]
    if not extension == '.h2pattern':
        raise TypeError('h2pattern_read can not read %d extension' % extension)

    tree = ET.parse(h2file)
    root = tree.getroot()

    # Get pattern
    xml_pattern = root.find('pattern')
    h2_pattern = H2Pattern(xml_pattern)

    # Get instruments and Drumkit
    drumkit_name = root.find('pattern_for_drumkit').text

    h2_data_path = '/usr/share/hydrogen/data/'
    h2_drumkits_path = os.path.join(h2_data_path, 'drumkits')
    drumkit_file = os.path.join(h2_drumkits_path, drumkit_name, 'drumkit.xml')

    drumkit = {'name': drumkit_name,
               'author': root.find('pattern_for_drumkit').text,
               'license': root.find('pattern_for_drumkit').text,
               'instruments': drumkit_read(drumkit_file)}

    return h2_pattern, drumkit


H2_Note = namedtuple('h2_Note', ['position', 'instrument'])


def drumkit_read(dk_file):
    """Read an Hydrogen drumkit file"""

    tree = ET.parse(dk_file)
    root = tree.getroot()
    instrumentList = root.find('instrumentList')
    instruments = dict()
    for instru in instrumentList.findall('instrument'):
        instru_id = int(instru.find('id').text)
        instruments[instru_id] = {'name': instru.find('name').text,
                                  'filename': instru.find('filename').text}
    return instruments


class H2Note(object):

    def __init__(self, position, instrument):
        self.position = position
        self.instrument = instrument

    def __eq__(self, other):
        return (self.position == other.position and
                self.instrument == other.instrument)

    def _neq__(self, other):
        return ((self.position != other.position) or
                (self.instrument != other.instrument))


class H2Pattern(object):
    def __init__(self, xml_pattern=None):
        if xml_pattern is not None:
            self.from_h2pattern(xml_pattern)
        else:
            self.name = ''
            self.notes = []
            self.category = ''
            self.instruments = set([])
            self.size = 0

    def add_note(self, position, instrument):
        h2note = H2Note(position=position,
                        instrument=instrument)
        self.notes.append(h2note)

    def from_h2pattern(self, xml_pattern):
        """
        Read a Hydrogen pattern
        """
    #        self.drumkit = drumkit_pattern.find('pattern_for_drumkit')
    #        self.author = drumkit_pattern.find('author')
    #        self.license = drumkit_pattern.find('license')
    #        pattern = drumkit_pattern.find('pattern')

        try:
            self.name = xml_pattern.find('pattern_name').text
        except AttributeError:
            self.name = xml_pattern.find('name').text

        self.category = xml_pattern.find('category').text

        self.size = int(xml_pattern.find('size').text)
    #        self.nb_beats = self.size // BEAT_LENGTH  # TODO check pattern length
    #        self.beat_per_measure = 4
    #        self.nb_measure = self.nb_beats // self.beat_per_measure
    #        self.measure_size = self.size // self.nb_measure
    #        self.nb_voices = 2
    #        print 'nb beats %d' % self.nb_beats
        # Initialize pattern
    #        self.pattern = Pattern(self.nb_measure, self.nb_voices)

    #        for measure in xrange(self.nb_measure):
    #            self.pattern.append([])
    #            for voice in mapVoice:
    #                self.pattern[-1].append([Note(REST, 0, self.size)])

        self.notes = []

        for note in xml_pattern.find('noteList').findall('note'):
            # length = note.find('length')
            self.add_note(position=int(note.find('position').text),
                          instrument=int(note.find('instrument').text))

        self.notes.sort()

        self.instruments = set([note.instrument for note in self.notes])

    def show(self):

        positions = set(self.notes.positions)
        pos_gcd = utils.gcd(positions)
        tab = [[' '] * (self.size / pos_gcd)
               for instru
               in xrange(max(self.instruments)+1)]
        for pos, instru in zip(self.notes.positions, self.notes.instruments):
            tab[instru][pos / pos_gcd] = 'x'
        print '\n'.join(['|'.join(line) for line in tab])
