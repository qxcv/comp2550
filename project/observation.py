"""Functions for parsing and representing external GPS and odometry
observations."""

from ast import literal_eval
from csv import DictReader

import numpy as np


DATA_HEADERS = (
    'lat', 'lon', 'alt', 'roll', 'pitch', 'yaw', 'vn', 've', 'vf', 'vl', 'vu',
    'ax', 'ay', 'az', 'af', 'al', 'au', 'wx', 'wy', 'wz', 'wf', 'wl', 'wu',
    'pos_accuracy', 'vel_accuracy', 'navstat', 'numsats', 'posmode', 'velmode',
    'orimode'
)


def coordinate_projector(reference_coords):
    """Returns a function which converts its supplied latitude and longitude to
    easting (in metres) and northing (in metres).

    Uses Mercator projection internally, hence the reference coordinates (used
    to derive scale factor to reduce distortion)."""
    ref_lat, ref_lon = reference_coords
    # Equatorial radius, in metres, derived from WGS84 ellipsoid, per Wikipedia
    earth_rad = 6378137
    # Combination of presumed radius of Earth and inverse Mercator scale factor
    # for ref latitude (like the size of the distortion ellipses!)
    pre_mult = earth_rad * np.cos(np.pi * ref_lat / 180.0)

    def inner(coords):
        lat, lon = coords
        x_rad = np.pi * lon / 180.0
        y_rad = np.log(np.tan(np.pi * (0.25 + lat / 360.0)))
        return np.array((pre_mult * x_rad, pre_mult * y_rad))

    return inner


class Observation(object):
    def __init__(self, time, pos, data):
        # Easting and northing are in metres
        self.pos = np.ndarray((2,))
        self.pos[0], self.pos[1] = pos

        # Time is seconds since some arbitrary point in the past
        self.time = time

        # Finally, store the complete data dictionary for reference
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return 'Observation({}, {}, {})'.format(
            self.time, self.pos, self.data
        )


def parse_map_trajectory(fp, freq=10, projector=None):
    """Generator returning series of observations from an iterable (presumed to
    be a file in the map trajectory format used by Brubaker et al)"""
    time = 0
    dt = 1.0 / freq
    for line in fp:
        data_dict = {k: v for k, v in zip(
            DATA_HEADERS,
            map(float, line.split())
        )}
        coords = (data_dict['lat'], data_dict['lon'])
        if projector is None:
            projector = coordinate_projector(coords)
        yield Observation(time, projector(coords), data_dict)
        time += dt


def parse_bool(s):
    rv = literal_eval(s)
    return bool(rv)


def parse_jose_map_trajectory(fp, projector=None):
    reader = DictReader(fp)
    for row in reader:
        data = {
            'signal': parse_bool(row['signal'])
        }
        for name in ('lat', 'lon', 'time'):
            data[name] = float(row[name])

        time = data['time']
        coords = (data['lat'], data['lon'])
        if projector is None:
            projector = coordinate_projector(coords)

        yield Observation(time, projector(coords), data)
