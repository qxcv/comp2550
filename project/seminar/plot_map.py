#!/usr/bin/env python2

"""Plot a nice image of map likelihood"""

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
import numpy as np

from os.path import abspath
from sys import path
path.append(abspath('../'))

from map import Map
from observation import coordinate_projector
from settings import KARLSRUHE_CENTER

# Samples per metre
SAMPLE_DENSITY = 1.0
EXTENTS = [612728, 613269, 4.11345e6, 4.11388e6]
EXTENTS = [612728, 613069, 4.11345e6, 4.11368e6]
MAP_PATH = '../data/kitti/00.osm.bz2'

if __name__ == '__main__':
    # Get map
    print("Loading map")
    proj = coordinate_projector(KARLSRUHE_CENTER)
    m = Map(MAP_PATH, proj)

    # Produce grid
    print("Producing grid")
    x_samples = int(EXTENTS[1] - EXTENTS[0] / SAMPLE_DENSITY)
    y_samples = int(EXTENTS[3] - EXTENTS[2] / SAMPLE_DENSITY)
    x_range = np.linspace(EXTENTS[0], EXTENTS[1], x_samples)
    y_range = np.linspace(EXTENTS[2], EXTENTS[3], y_samples)
    X, Y = np.meshgrid(x_range, y_range)

    # Take samples
    print("Sampling")
    dists = np.zeros((y_samples, x_samples))
    for i in xrange(x_samples):
        for j in xrange(y_samples):
            pos = (X[j, i], Y[j, i])
            dists[j, i] = m.nearest_lane_dist(pos)
    results = np.log(1.0 / (1 + dists**2))

    # Plot
    print("Plotting")
    # ax = plt.figure().gca(projection='3d')
    # ax.plot_surface(X, Y, results, cmap='coolwarm')
    plt.imshow(results, extent=EXTENTS).set_cmap('gist_heat')
    plt.colorbar()
    plt.xlabel('$x$-coordinate (m)')
    plt.ylabel('$y$-coordinate (m)')
    plt.title(r'$\log(p((x, y) \mid\,\mathrm{map}))$')
    plt.tight_layout()
    plt.savefig('images/map-likelihood.png')
