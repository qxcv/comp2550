"""Functions for parsing and representing external GPS and odometry
observations."""


import numpy as np


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
        return pre_mult * x_rad, pre_mult * y_rad

    return inner


class Observation(object):
    def __init__(self, pos, coords, time):
        # Easting and northing are in metres
        self.pos = np.ndarray((2,))
        self.pos[0], self.pos[1] = pos

        # Latitude and longitude are in degrees, decimal format
        self.coords = np.ndarray((2,))
        self.coords[0], self.coords[1] = coords

        # Time is seconds since some arbitrary point in the past
        self.time = time


def parse_map_trajectory(fp, freq=10):
    # Generator returning series of observations from an iterable (presumed to
    # be a file in the map trajectory format used by Brubaker et al)
    time = 0
    dt = 1.0 / freq
    projector = None
    for line in fp:
        coords = tuple(map(float, line.split()[:2]))
        if projector is None:
            projector = coordinate_projector(coords)
        yield Observation(projector(coords), coords, time)
        time += dt
