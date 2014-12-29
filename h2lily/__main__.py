# -*- coding: utf-8 -*-


"""h2lily.__main__: executed when h2lily directory is called as script."""
from h2lily.h2lily import main, __doc__
from docopt import docopt

options = docopt(__doc__, version='0.1')

main(options)
