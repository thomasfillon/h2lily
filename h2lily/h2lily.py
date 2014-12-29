#! /usr/bin/env python
"""H2Lily.

Usage:
  h2lily.py <h2file>
  h2lily.py <h2file> [--show-instruments --header]
  h2lily.py -h | --help
  h2lily.py --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  --show-instruments   Show instrument in pattern drumkit
  --header             Add header
"""


# see
#  http://gehrcke.de/2014/02/distributing-a-python-command-line-application/
#  https://www.youtube.com/watch?v=pXhcPJK5cMc
#  http://docopt.org/
from docopt import docopt

from .core import Pattern, Voice_Config, Voices_Set, UP, DOWN
from .hydrogen import h2pattern_read
from .lilypond import makeHeader

import os.path
import subprocess


def main():
    arguments = docopt(__doc__, version='0.1')
    voice_up = Voice_Config(name='Up', instruments=[6, 11, 12],
                            stem_direction=UP)

    voice_down = Voice_Config(name='Down', instruments=[0, 2, 4],
                              stem_direction=DOWN)
    #voice_down2 = Voice_Config(name='Down2', instruments=[0], stem_direction=DOWN)

    voices = Voices_Set()
    voices._add_voice(voice_up)
    voices._add_voice(voice_down)
    #voices._add_voice(voice_down2)

    h2file = arguments["<h2file>"]

    if not os.path.exists(h2file):
        raise ValueError('No such file %s' % h2file)
    extension = os.path.splitext(h2file)[1]

    if extension == '.h2pattern':
        h2_pattern, drumkit = h2pattern_read(h2file)
    elif extension == '.h2song':
        #  TODO  : Implement h2song reader
        raise NotImplementedError

    pattern = Pattern(h2_pattern=h2_pattern, voices=voices)

    if arguments['--show-instruments']:
        instruments = {instru: drumkit['instruments'][instru]['name']
                       for instru
                       in h2_pattern.instruments}
        print '--------------------'
        print '--show-instruments--'
        print '--------------------'
        print "Instruments in Drumkit \"%s\":" % drumkit['name']
        for key, value in instruments.items():
            print "%d:\t%s" % (key, value)
        print '--------------------'
        return

    if arguments["--header"]:
        header = makeHeader()
    else:
        header = ''

    # Patterns definition
    PatternDefinition = ('%% -- Patterns definition --\n'
                         '{}').format(pattern.to_lily())

    drumScore = '%% -- Score --\ndrumScore = {\n\t\\%s\n}\n' % pattern.lily_name

    drumStaff = """\\new DrumStaff <<
        \\tempo 4=102
        \\time 4/4
        \\set Timing.baseMoment = #(ly:make-moment 1 8)
        \\set Timing.beatStructure = #'(2 2 2 2)
        \\set Timing.beamExceptions = #'()
    """
    for i in range(len(voices)):
        drumStaff += '    \\new DrumVoice = "%d" { s1 *4 }\n' % i

    drumStaff += '    \\drumScore\n>>'

    lilyDoc = '\n'.join([header, PatternDefinition, drumScore, drumStaff])
    ly_name = os.path.split(h2file)[1] + '.ly'

    print "---> %s" % ly_name
    with open(ly_name, 'w+') as ly_file:
        ly_file.write(lilyDoc)

    command = ['lilypond', ly_file.name]
    stdout = subprocess.check_output(command)

if __name__ == "__main__":
    options = docopt(__doc__, version='0.1')
    main(options)
