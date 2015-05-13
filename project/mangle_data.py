#!/usr/bin/env python2

"""Can be used to produce pretty plots and summary statistics from the .csv
files produced by run.py"""

from argparse import ArgumentParser

import pandas as pd

from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument('data', type=open, help="Data CSV to read from")
parser.add_argument(
    '--graph', action='store_true', default=False,
    help="Display an informative graph from the data."
)
parser.add_argument(
    '--rawgps', action='store_true', default=False,
    help="Calculate figures for raw GPS"
)
parser.add_argument(
    '--mapfilter', action='store_true', default=False,
    help="Calculate figures for map-based filter"
)
parser.add_argument(
    '--plainfilter', action='store_true', default=False,
    help="Calculate figures for plain filter"
)

if __name__ == '__main__':
    args = parser.parse_args()
    data = pd.read_csv(args.data)

    assert args.rawgps or args.mapfilter or args.plainfilter

    if args.rawgps:
        print("Summary statistics for raw GPS:")
        print(data['gps_hpe'].describe())
    if args.mapfilter:
        print("Summary statistics for map-based PF:")
        print(data['map_hpe'].describe())
    if args.plainfilter:
        print("Summary statistics for plain PF:")
        print(data['plain_hpe'].describe())

    if args.graph:
        plt.title("Horizontal positioning error over time")
        plt.xlabel("Time (s)")
        plt.ylabel("Positioning error (m)")
        if args.rawgps:
            plt.plot(data['time'], data['gps_hpe'], 'b-', label="Raw GPS")
        if args.mapfilter:
            plt.plot(data['time'], data['map_hpe'], 'r-', label="Map PF")
        if args.plainfilter:
            plt.plot(data['time'], data['plain_hpe'], 'g-',
                     label="PF (no map)")
        plt.legend()
        plt.xlim(xmin=0, xmax=max(data['time']))
        plt.show()
