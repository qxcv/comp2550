#!/bin/bash

# See how long the algorithm takes with and without map information for
# different numbers of particles

PARTICLE_COUNTS=`echo {500..2000..500}`
RUN="python2 run.py"
DEST_DIR=results/

mkdir -p "$DEST_DIR"

for id in {00..10}; do
    trajectory=data/kitti/map_trajectories/${id}.txt.bz2
    map=data/kitti/${id}.osm.bz2
    echo "Attempting times for trajectory $id"
    set -x
    $RUN --enablemapfilter --out "$DEST_DIR/${id}-map.csv" \
        "$trajectory" "$map" &
    set +x
    child_block
    set -x
    $RUN --enableplainfilter --out "$DEST_DIR/${id}-plain.csv" \
        "$trajectory" "$map" &
    set +x
    echo "Spawning for $id done"
    sleep 2
done
