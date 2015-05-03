#!/usr/bin/env python

from argparse import ArgumentParser
from random import random

from matplotlib import pyplot as plt

from graphics import mpl_draw_map, plot_particle
from observation import parse_map_trajectory, coordinate_projector
from map import Map
from settings import KARLSRUHE_CENTER

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
    mpl_draw_map(m)

    for obs in parsed:
        # Randomly skip 90% of points
        if random() < 0.9:
            continue
        plot_particle(obs.pos, obs['yaw'], random())

    plt.show()
