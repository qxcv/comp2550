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

if __name__ == '__main__':
    args = parser.parse_args()
    data = pd.read_csv(args.data)

    print(data['hpe'].describe())

    if args.graph:
        plt.title("Horizontal positioning error over time")
        plt.plot(data['time'], data['hpe'], 'b-')
        plt.xlabel("Time (s)")
        plt.ylabel("Positioning error (m)")
        plt.show()
