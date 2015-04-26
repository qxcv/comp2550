#!/usr/bin/env python3

from argparse import ArgumentParser

import numpy as np

from observation import parse_map_trajectory

parser = ArgumentParser()
parser.add_argument('data_fp', type=open)
parser.add_argument('--freq', type=int, default=10)

if __name__ == '__main__':
    args = parser.parse_args()
    parsed = parse_map_trajectory(args.data_fp, args.freq)
    last_pos = None
    # Just some fun code :-)
    for obs in parsed:
        if last_pos is not None:
            new_x, new_y = obs.pos
            old_x, old_y = last_pos
            dist = np.sqrt((new_x - old_x) ** 2 + (new_y - old_y) ** 2)
            speed = dist * args.freq
            print("Speed: {}km/h".format(speed * 3.6))
        last_pos = obs.pos
