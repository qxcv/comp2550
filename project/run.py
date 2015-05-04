#!/usr/bin/env python

from argparse import ArgumentParser

from matplotlib import pyplot as plt

from graphics import mpl_draw_map, plot_particle, plot_vehicle_tri
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
    dt = 1.0 / args.freq
    disable_for = 0
    proj = coordinate_projector(KARLSRUHE_CENTER)
    parsed = parse_map_trajectory(args.data_fp, args.freq, proj)
    m = Map(args.map_path, proj)
    f = None

    plt.ion()
    mpl_draw_map(m)
    plt.show()

    for obs in parsed:
        backup_axes = (plt.xlim(), plt.ylim())

        if not disable_for:
            plt.clf()
            plt.xlim(backup_axes[0])
            plt.ylim(backup_axes[1])
            mpl_draw_map(m)

        # TODO: Noise, estimated location, HPE
        # TODO: NOOOOO, this doesn't take into account the fact that we're
        # missing SOOO MANY intermediate observations :(
        if f is None:
            f = ParticleFilter(500, obs.pos, 10)
        else:
            f.measure_gps(obs.pos, 10)
            f.auto_resample()
            f.predict(dt, obs['vf'], obs['wu'])
            f.normalise_weights()

        if not disable_for:
            for i in xrange(f.num_points):
                plot_particle(
                    f.coords[i], f.yaws[i], f.weights[i] * f.num_points
                )

        if not disable_for:
            plot_vehicle_tri(obs.pos, obs['yaw'], (0, 1, 0, 0.8))
            pred_x, pred_y, pred_yaw = f.state_estimate()
            plot_vehicle_tri((pred_x, pred_y), pred_yaw)

            plt.draw()

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
