"""Classes and utilities for illustrating particle filters."""

from math import cos, sin, pi

from matplotlib import patches, pyplot as plt

# Maximum particle radius, in metres
MAX_PARTICLE_RAD = 5


def mpl_draw_map(map, region=None):
    for begin, end in map.segments:
        plt.plot((begin[0], end[0]), (begin[1], end[1]), 'b-')


def plot_particle(coords, heading=0, weight=1):
    radius = MAX_PARTICLE_RAD * weight
    circ = patches.Circle(coords, radius)
    angle = pi / 2.0 - heading
    line_end = (coords[0] + radius*cos(angle), coords[1] + radius*sin(angle))
    plt.plot((coords[0], line_end[0]), (coords[1], line_end[1]))
    plt.gca().add_patch(circ)
