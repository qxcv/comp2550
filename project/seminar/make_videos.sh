#!/usr/bin/env bash

# Kill children on exit
trap 'kill $(jobs -pr)' EXIT

# This will take an excruciatingly long time, since matplotlib is *incredibly*
# slow at drawing the map and all of the particles.
../run.py ../data/kitti/map_trajectories/01.txt.bz2 ../data/kitti/01.osm.bz2 \
    --particles 2000 --enablemapfilter --movie with-map.webm &
../run.py ../data/kitti/map_trajectories/01.txt.bz2 ../data/kitti/01.osm.bz2 \
    --particles 2000 --enableplainfilter --movie without-map.webm &
wait
