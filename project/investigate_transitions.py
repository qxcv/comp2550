#!/usr/bin/env python2

"""Program to investigate the transition distribution $p(z_{n+1} \mid z_n)$
for the available map trajectories.

Usage: <program name> <trajectory> [<trajectory> [...]]"""

from collections import defaultdict
from sys import argv

from matplotlib import pyplot as plt

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
    vf_diff = vf_pairs[:, 1] - vf_now
    hist, x_edges, y_edges = np.histogram2d(vf_now, vf_diff, bins=50)
    pc_x, pc_y = np.meshgrid(x_edges, y_edges)
    # Normalise columns
    # sums = np.sum(hist, axis=0)
    # sums[sums == 0] = 1
    # hist /= sums

    plt.pcolormesh(pc_x, pc_y, hist)
    plt.xlabel('$v_f$ (m/s)')
    plt.ylabel("$v_f' - v_f$ (m/s)")
    plt.xlim(x_edges[0], x_edges[-1])
    plt.ylim(y_edges[0], y_edges[-1])
    plt.title("Transition frequencies for forward velocity ($v_f$)")

    plt.show()
