""" Base module for parsing ISO 6709 formatted data """

import re
from decimal import Decimal


def coords_to_dms_degree(raw_coords):
    """ Convert a string of coordinates to a set of DMSDegree and Decimal Altitude """
    re_coord = r"""
                ^
                (?P<lat_sign>\+|-)
                (?P<lat_degrees>[0,1]?\d{2})
                (?P<lat_minutes>\d{2}?)?
                (?P<lat_seconds>\d{2}?)?
                (?P<lat_fraction>\.\d+)?
                (?P<lng_sign>\+|-)
                (?P<lng_degrees>[0,1]?\d{2})
                (?P<lng_minutes>\d{2}?)?
                (?P<lng_seconds>\d{2}?)?
                (?P<lng_fraction>\.\d+)?
                (?P<alt>[\+\-]\d+)?
    """
    regex = re.compile(re_coord, flags=re.VERBOSE)
    match = regex.match(raw_coords).groupdict()
    results = {}
    for key in ('lat', 'lng'):
        results[key] = {}
        for value in ('sign', 'degrees', 'minutes', 'seconds', 'fraction'):
            results[key][value] = match['{}_{}'.format(key, value)]

    alt = Decimal(match['alt']) if match['alt'] is not None else Decimal(0)
    return DMSDegree(**results['lat']), DMSDegree(**results['lng']), alt


class DMSDegree(object):
    """ An object representing a DMS Degree """

    def __init__(self, degrees, minutes=None, seconds=None, fraction=None, sign=None):
        if fraction is not None:
            if seconds is not None:
                seconds += fraction
            elif minutes is not None:
                minutes += fraction
            else:
                degrees += fraction
        minutes = Decimal(minutes) if (minutes is not None) else 0
        seconds = Decimal(seconds) if (seconds is not None) else 0
        degrees = Decimal(degrees)
        decimal = degrees + minutes / Decimal('60') + seconds / Decimal('3600')
        decimal = decimal * Decimal(sign + '1')

        self.degrees, self.minutes, self.seconds, self.sign = degrees, minutes, seconds, sign
        self.decimal = decimal


class Location(object):
    """ A class for parsing and returning data from an ISO 6709 standard string."""

    def __init__(self, raw_coords):
        self.raw_coords = raw_coords
        self.lat, self.lng, self.alt = coords_to_dms_degree(raw_coords)