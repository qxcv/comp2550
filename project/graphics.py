"""Classes and utilities for illustrating particle filters."""

from math import cos, sin, sqrt, pi

from matplotlib import patches, transforms, pyplot as plt

# Maximum particle radius, in metres
MAX_PARTICLE_RAD = 5


def mpl_draw_map(map, region=None):
    for begin, end in map.segments:
        plt.plot((begin[0], end[0]), (begin[1], end[1]), 'b-')


def plot_vehicle_tri(coords, yaw, color=(0, 0, 1, 0.5)):
    """Plot a marker representing a vehicle (either ground truth or
    estimate)"""
    vertices = [
        [0, 0],
        [0.77, -0.5],
        [0, 0.5],
        [-0.77, -0.5]
    ]
    tri = patches.Polygon(
        vertices, closed=True, facecolor=color, edgecolor=(0, 0, 0),
    )
    ax = plt.gca()
    tri.set_transform(transforms.Affine2D()
                                .scale(10)
                                .rotate(yaw - pi/2)
                                .translate(*coords)
                      + ax.transData)
    ax.add_patch(tri)


def plot_particle(coords, yaw=0, weight=1):
    """Plot a particle at the given Cartesian coordinates, with radius
    determined by weight. Note that "yaw" is in radians, counterclockwise from
    east (i.e. east is 0 rad, north is pi/2 rad, west is pi rad, south is 3pi/2
    rad, etc.). This is consistent with the OxTS unit output convention."""
    # Significance of sqrt is that it makes circle areas proportional to weight
    radius = MAX_PARTICLE_RAD * sqrt(weight)
    circ = patches.Circle(
        coords, radius, facecolor=(1, 0, 0, 0.2), edgecolor='r'
    )
    line_end = (coords[0] + radius*cos(yaw), coords[1] + radius*sin(yaw))
    plt.plot(
        (coords[0], line_end[0]), (coords[1], line_end[1]), color=(0, 0, 0)
    )
    plt.gca().add_patch(circ)
