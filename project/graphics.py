"""Classes and utilities for illustrating particle filters."""

from matplotlib import pyplot as plt


def mpl_draw_map(map, region=None):
    for begin, end in map.segments:
        plt.plot((begin[0], end[0]), (begin[1], end[1]), 'b-')


def plot_particle(coords):
    pass
