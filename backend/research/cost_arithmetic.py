"""DEV exact accumulation of already-rounded binary64 geometric primitives.

This does not make Euclidean distances/geometry exact or set research tolerance.
"""

from fractions import Fraction
from math import isfinite, nextafter, inf

COST_POLICY = 'tv4-dev-dyadic-primitive-cost-v1'


def weighted_cost(down, up, cycles, theta):
    if not all(isfinite(v) for v in (down, up, theta.rho, theta.lambda_mm)):
        raise ValueError('Non-finite cost primitive')
    return (Fraction(down) + Fraction(theta.rho) * Fraction(up)
            + Fraction(theta.lambda_mm) * cycles)


def rounded_cost(value):
    try:
        result = float(value)
    except OverflowError:
        raise ValueError('Non-finite cost output') from None
    if not isfinite(result):
        raise ValueError('Non-finite cost output')
    return result


def cost_interval(value):
    """Outward binary64 enclosure of the dyadic value, not a geometry error bound."""
    nearest = rounded_cost(value)
    represented = Fraction(nearest)
    bounds = (nextafter(nearest, -inf) if represented > value else nearest,
              nextafter(nearest, inf) if represented < value else nearest)
    if not all(isfinite(v) for v in bounds):
        raise ValueError('Non-finite cost enclosure')
    return bounds
