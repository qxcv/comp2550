#!/usr/bin/env python

from argparse import ArgumentParser
from itertools import islice

from matplotlib import pyplot as plt

from graphics import mpl_draw_map, plot_particle
from observation import parse_map_trajectory, coordinate_projector
from map import Map
from settings import KARLSRUHE_CENTER
from filter import ParticleFilter

parser = ArgumentParser()
parser.add_argument('data_fp', type=open)
parser.add_argument('map_path', type=str,
                    help="Path to a .osm file containing map data")
parser.add_argument('--freq', type=int, default=10)

if __name__ == '__main__':
    args = parser.parse_args()
    proj = coordinate_projector(KARLSRUHE_CENTER)
    parsed = parse_map_trajectory(args.data_fp, args.freq, proj)

    # Just some fun code :-)
    m = Map(args.map_path, proj)

    f = None

    plt.ion()
    mpl_draw_map(m)
    plt.show()

    for obs in islice(parsed, None, None, args.freq):
        backup_axes = (plt.xlim(), plt.ylim())
        plt.clf()
        plt.xlim(backup_axes[0])
        plt.ylim(backup_axes[1])
        mpl_draw_map(m)
        if f is None:
            f = ParticleFilter(100, obs.pos, 10)
        else:
            f.measure_gps(obs.pos, 10)
            f.auto_resample()
            f.predict(obs['vf'], obs['wu'])
            f.normalise_weights()

        for i in xrange(f.num_points):
            plot_particle(f.coords[i], f.yaws[i], f.weights[i] * f.num_points)

        plt.draw()
        raw_input("Hit <enter> for next frame")
