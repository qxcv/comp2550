#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from csv import writer
from sys import stdin, exit
from termios import tcflush, TCIFLUSH
from bz2 import BZ2File

import numpy as np

from matplotlib import pyplot as plt

from filter import ParticleFilter
from graphics import MapDisplay
from map import Map, JoseMap
from noise import noisify
from observation import (parse_map_trajectory, coordinate_projector,
                         parse_jose_map_trajectory)
from settings import KARLSRUHE_CENTER


class StatsWriter(object):
    """Class for writing statistics to a file pointer"""
    def __init__(self, fp, enable_map_f=False, enable_plain_f=False,
                 enable_raw_gps=False):
        self.writer = writer(fp)

        labels = [
            "time", "true_x", "true_y", "true_yaw"
        ]

        if enable_map_f:
            labels += ["map_pred_x", "map_pred_y", "map_pred_yaw", "map_hpe"]
        if enable_plain_f:
            labels += ["plain_pred_x", "plain_pred_y", "plain_pred_yaw",
                       "plain_hpe"]
        if enable_raw_gps:
            labels += ["gps_pred_x", "gps_pred_y", "gps_hpe"]

        self.writer.writerow(labels)

    def filter_columns(self, obs, f):
        """Calculates predicted X, predicted Y, predicted yaw and HPE for a
        filter, given some ground truth observation."""
        pred_x, pred_y, pred_yaw = f.state_estimate()
        pred_yaw = pred_y
        return [
            pred_x, pred_y, pred_yaw,
            self.hpe(obs.pos, (pred_x, pred_y))
        ]

    def hpe(self, truth, guess):
        pred_x, pred_y = guess
        true_x, true_y = truth
        return np.sqrt((true_x-pred_x)**2 + (true_y-pred_y)**2)

    def update(self, obs, map_f=None, plain_f=None, last_fix=None):
        """Take a filter and an observation and write a new line to the output
        file"""
        true_x, true_y = obs.pos
        true_yaw = obs['yaw']
        columns = [obs.time, true_x, true_y, true_yaw]

        if map_f is not None:
            columns += self.filter_columns(obs, map_f)
        if plain_f is not None:
            columns += self.filter_columns(obs, plain_f)
        if last_fix is not None:
            columns += [last_fix[0], last_fix[1], self.hpe(obs.pos, last_fix)]

        self.writer.writerow(columns)


def update_filter(f, obs, dt, give_fix=False, m=None):
    if give_fix:
        f.gps_update(obs.pos, 10)
    f.auto_resample()
    if m is not None:
        f.map_update(m)
    f.auto_resample()
    # In the first step, dt will be None
    if dt is not None:
        if f.have_imu:
            f.predict(dt, obs['vf'], obs['wu'])
        else:
            f.predict(dt)
    f.normalise_weights()

parser = ArgumentParser()
parser.add_argument(
    'data_path', type=str, help="Map trajectory to read from"
)
parser.add_argument(
    'map_path', type=str, help="Path to a .osm file containing map data"
)
parser.add_argument(
    '--out', type=FileType('w'), default=None,
    help="File to write particle filter estimates and ground truth to"
)
parser.add_argument(
    '--jose', action='store_true', default=False,
    help="Use Jose's data format (CSV trace, .mat map)"
)
parser.add_argument(
    '--freq', type=int, default=10,
    help="Frequency of observations in the supplied data set"
)
parser.add_argument(
    '--gpsfreq', type=float, default=1,
    help="Frequency at which GPS observations will be used"
)
parser.add_argument(
    '--gpsstddev', type=float, default=4,
    help="Standard deviation of white GPS noise"
)
parser.add_argument(
    '--speederror', type=float, default=0.025,
    help="Speed estimates accurate to 100*speederror percent"
)
parser.add_argument(
    '--gyrostddev', type=float, default=0.05,
    help="Standard deviation of gyroscope noise (deg/s)"
)
parser.add_argument(
    '--gui', action='store_true', default=False, help="Enable GUI"
)
parser.add_argument(
    '--particles', type=int, default=100, help="Number of particles to use"
)
parser.add_argument(
    '--enablemapfilter', action='store_true', default=False,
    help="Run filtering with map information"
)
parser.add_argument(
    '--enableplainfilter', action='store_true', default=False,
    help="Run filtering without a map"
)
parser.add_argument(
    '--enablerawgps', action='store_true', default=False,
    help="Attempt localisation using only GPS fixes"
)
parser.add_argument(
    '--noimu', action='store_true', default=False,
    help="Should the IMU be disabled for the map filter?"
)

if __name__ == '__main__':
    args = parser.parse_args()
    disable_for = 0
    proj = coordinate_projector(KARLSRUHE_CENTER)
    if args.data_path.endswith('.bz2'):
        trajectory_fp = BZ2File(args.data_path)
    else:
        trajectory_fp = open(args.data_path, 'rb')
    if args.jose:
        assert args.noimu, "Jose's data has no IMU info; use --noimu"
        parsed = parse_jose_map_trajectory(trajectory_fp, proj)
        m = JoseMap(args.map_path, proj)
    else:
        parsed = parse_map_trajectory(trajectory_fp, args.freq, proj)
        m = Map(args.map_path, proj)
    map_f = None
    plain_f = None

    obs_per_fix = int(round(args.freq / float(args.gpsfreq)))
    if obs_per_fix < 1:
        print("Due to --gpsfreq {}, no GPS samples will be included!".format(
            args.gpsfreq
        ))
        obs_per_fix = 0

    if args.gui:
        display = MapDisplay(m)

    if args.out is not None:
        stats_writer = StatsWriter(
            args.out,
            enable_map_f=args.enablemapfilter,
            enable_plain_f=args.enableplainfilter,
            enable_raw_gps=args.enablerawgps
        )

    obs_since_fix = 0
    last_fix = None
    last_time = None
    noisified = noisify(
        parsed, args.gpsstddev, args.speederror, args.gyrostddev
    )

    assert not args.noimu or args.enablemapfilter, "Map filter must be " \
        "enabled for --noimu to take effect"

    for obs, noisy_obs in noisified:
        if last_time is not None:
            dt = obs.time - last_time
        else:
            dt = None
        last_time = obs.time

        if last_fix is None and args.enablerawgps:
            last_fix = noisy_obs.pos

        give_fix = obs_since_fix >= obs_per_fix
        if give_fix:
            if last_fix is not None:
                last_fix = noisy_obs.pos
            obs_since_fix = 1
            if args.gui:
                display.update_last_fix(noisy_obs.pos)
        else:
            obs_since_fix += 1

        if args.enablemapfilter and map_f is None:
            map_f = ParticleFilter(
                args.particles, noisy_obs.pos, 5, have_imu=not args.noimu
            )
        elif map_f is not None:
            update_filter(map_f, noisy_obs, dt, give_fix, m)

        if args.enableplainfilter and plain_f is None:
            plain_f = ParticleFilter(args.particles, noisy_obs.pos, 5)
        elif plain_f is not None:
            update_filter(plain_f, noisy_obs, dt, give_fix)

        if args.gui and not disable_for:
            # Make a list of filters for the display to update
            filters = []
            if plain_f is not None:
                filters.append(plain_f)
            if map_f is not None:
                filters.append(map_f)

            if filters:
                display.update_filters(filters)

            display.update_ground_truth(
                obs.pos, obs['yaw'] if 'yaw' in obs else None
            )
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
            stats_writer.update(
                obs, map_f=map_f, plain_f=plain_f,
                last_fix=last_fix
            )
