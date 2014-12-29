# -*- coding: utf-8 -*-

import fractions


def gcd(numbers):
    """Return the Greatest Common Divisor of a list of integers
    """

    return reduce(fractions.gcd, numbers)
