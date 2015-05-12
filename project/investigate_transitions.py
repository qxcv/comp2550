#!/usr/bin/env python2

"""Program to investigate the transition distribution $p(z_{n+1} \mid z_n)$
for the available map trajectories.

Usage: <program name> <trajectory> [<trajectory> [...]]"""

from collections import defaultdict
from sys import argv

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

import numpy as np

from observation import parse_map_trajectory

if __name__ == '__main__':
    assert len(argv) > 1, "Need at least one input file"

    pairs = defaultdict(lambda: [])

    for filename in argv[1:]:
        with open(filename) as fp:
            traj = list(parse_map_trajectory(fp))
            for past, present in zip(traj, traj[1:]):
                for key in past.data.iterkeys():
                    pairs[key].append((past[key], present[key]))

    vf_pairs = np.array(pairs['vf'])
    vf_now = vf_pairs[:, 0]
    vf_next = vf_pairs[:, 1]
    # Adapted from http://matplotlib.org/examples/mplot3d/hist3d_demo.html
    hist, x_edges, y_edges = np.histogram2d(vf_now, vf_next, bins=50)
    elems = (len(x_edges) - 1) * (len(y_edges) - 1)
    xpos, ypos = np.meshgrid(x_edges[:-1], y_edges[:-1])

    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros(elems)
    dx = np.ones_like(zpos)
    dy = np.ones_like(zpos)
    dz = hist.flatten()

    ax = plt.gcf().add_subplot(111, projection='3d')
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz)
    ax.set_xlabel('Current $v_f$')
    ax.set_ylabel('Next $v_f$')
    ax.set_zlabel('Frequency')

    plt.show()
