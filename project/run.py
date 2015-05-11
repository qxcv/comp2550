#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from csv import writer
from sys import stdin, exit
from termios import tcflush, TCIFLUSH

import numpy as np

from matplotlib import pyplot as plt

from filter import ParticleFilter
from graphics import MapDisplay
from map import Map
from noise import noisify
from observation import parse_map_trajectory, coordinate_projector
from settings import KARLSRUHE_CENTER


class StatsWriter(object):
    """Class for writing statistics to a file pointer"""
    def __init__(self, fp, dt):
        self.writer = writer(fp)
        self.writer.writerow([
            "time", "true_x", "true_y", "true_yaw", "pred_x",
            "pred_y", "pred_yaw", "hpe"
        ])
        self.seconds = 0
        self.dt = dt

    def add_gps_fix(obs):
        pass

    def update(self, f, obs):
        """Take a filter and an observation and write a new line to the output
        file"""
        pred_x, pred_y, pred_yaw = f.state_estimate()
        pred_yaw = pred_y
        true_x, true_y = obs.pos
        true_yaw = obs['yaw']
        self.writer.writerow([
            self.seconds, true_x, true_y, true_yaw, pred_x, pred_y,
            pred_yaw, np.sqrt((true_x-pred_x)**2 + (true_y-pred_y)**2)
        ])
        self.seconds += dt

parser = ArgumentParser()
parser.add_argument('data_fp', type=open, help="Map trajectory to read from")
parser.add_argument('map_path', type=str,
                    help="Path to a .osm file containing map data")
parser.add_argument(
    '--out', type=FileType('w'), default=None,
    help="File to write particle filter estimates and ground truth to"
)
parser.add_argument('--freq', type=int, default=10,
                    help="Frequency of observations in the supplied data set")
parser.add_argument('--gpsfreq', type=int, default=1,
                    help="Frequency at which GPS observations will be used")
parser.add_argument('--gpsstddev', type=float, default=4,
                    help="Standard deviation of white GPS noise")
parser.add_argument('--gpsstep', type=float, default=1,
                    help="Max drift per second for brownian GPS noise")
parser.add_argument('--speederror', type=float, default=0.025,
                    help="Speed estimates accurate to 100*speederror%")
parser.add_argument('--gyrostddev', type=float, default=0.05,
                    help="Standard deviation of gyroscope noise (deg/s)")
parser.add_argument('--gui', action='store_true', default=False,
                    help="Enable GUI")
parser.add_argument('--particles', type=int, default=100,
                    help="Number of particles to use")
parser.add_argument('--disablemap', action='store_true', default=False,
                    help="Disable use of map information")
parser.add_argument('--enablemapfilter', action='store_true', default=False,
                    help="Run filtering with map information")
parser.add_argument('--enablenomapfilter', action='store_true', default=False,
                    help="Run filtering without a map")
parser.add_argument('--enablerawgps', action='store_true', default=False,
                    help="Attempt localisation using only GPS fixes")

if __name__ == '__main__':
    args = parser.parse_args()
    dt = 1.0 / args.freq
    disable_for = 0
    proj = coordinate_projector(KARLSRUHE_CENTER)
    parsed = parse_map_trajectory(args.data_fp, args.freq, proj)
    m = Map(args.map_path, proj)
    f = None

    obs_per_fix = int(round(args.freq / float(args.gpsfreq)))
    if obs_per_fix < 1:
        print("Due to --gpsfreq {}, no GPS samples will be included!".format(
            args.gpsfreq
        ))
        obs_per_fix = 0

    if args.gui:
        display = MapDisplay(m)

    if args.out is not None:
        stats_writer = StatsWriter(args.out, dt)

    obs_since_fix = 0
    noisified = noisify(
        parsed, args.gpsstddev, args.gpsstep * dt, args.speederror,
        args.gyrostddev
    )
    for obs, noisy_obs in noisified:
        if f is None:
            f = ParticleFilter(args.particles, noisy_obs.pos, 5)
        else:
            if obs_per_fix and obs_since_fix >= obs_per_fix:
                f.measure_gps(noisy_obs.pos, 10)
                obs_since_fix = 1
                if args.gui:
                    display.update_last_fix(noisy_obs.pos)
            else:
                obs_since_fix += 1

            f.auto_resample()

            if not args.disablemap:
                f.measure_map(m)

            f.auto_resample()

            f.predict(dt, noisy_obs['vf'], noisy_obs['wu'])

            f.normalise_weights()

        if args.gui and not disable_for:
            display.update_filter(f)
            display.update_ground_truth(obs.pos, obs['yaw'])
            display.redraw()

            while True:
                # Interaction code
                tcflush(stdin, TCIFLUSH)
                d_str = raw_input("Command (enter for next frame): ").strip()
                if not d_str:
                    break

                split = d_str.split()
                cmd = split[0]
                opts = split[1:]

                if cmd in ['n', 'next']:
                    if not opts:
                        break

                    try:
                        disable_for_s, = opts
                        disable_for = int(disable_for_s)
                        break
                    except ValueError:
                        print(
                            "Invalid argument to 'next'. Please either supply "
                            "a number of steps to skip or no argument at all."
                        )
                elif cmd in ['c', 'continue']:
                    disable_for = -1
                    break
                elif cmd in ['q', 'quit']:
                    plt.close('all')
                    exit(0)

                print("Unkown command {}"
                      .format(cmd))

        if disable_for > 0:
            disable_for -= 1

        if args.out is not None:
            stats_writer.update(f, obs)
