#!/usr/bin/env python

from argparse import ArgumentParser

from matplotlib import pyplot as plt

from graphics import MapDisplay
from observation import parse_map_trajectory, coordinate_projector
from map import Map
from settings import KARLSRUHE_CENTER
from filter import ParticleFilter

parser = ArgumentParser()
parser.add_argument('data_fp', type=open)
parser.add_argument('map_path', type=str,
                    help="Path to a .osm file containing map data")
parser.add_argument('--freq', type=int, default=10)
parser.add_argument('--gpsfreq', type=int, default=1)
parser.add_argument('--gpsnoise', action='store_true', default=False)
parser.add_argument('--odomnoise', action='store_true', default=False)
parser.add_argument('--gyronoise', action='store_true', default=False)
parser.add_argument('--gui', action='store_true', default=False)

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
    else:
        print("Will throw in a GPS sample every {} time steps.".format(
            obs_per_fix
        ))

    if args.gui:
        display = MapDisplay(m)

    obs_since_fix = 0
    for obs in parsed:
        # TODO: Noise, estimated location, HPE
        if f is None:
            f = ParticleFilter(500, obs.pos, 10)
        else:
            if obs_per_fix and obs_since_fix >= obs_per_fix:
                f.measure_gps(obs.pos, 10)
                obs_since_fix = 1
            else:
                obs_since_fix += 1
            f.auto_resample()
            f.predict(dt, obs['vf'], obs['wu'])
            f.normalise_weights()

        if args.gui and not disable_for:
            display.update_filter(f)
            display.update_ground_truth(obs.pos, obs['yaw'])
            display.redraw()

            d_str = raw_input("Hit [number of frames to skip] <enter> for "
                              "next frame ")
            try:
                disable_for = int(d_str)
            except ValueError:
                pass

        if disable_for > 0:
            disable_for -= 1
        else:
            disable_for = 0
