#!/bin/bash

# Run over all of the given examples and produce some nice CSVs

COMMON_OPTIONS="--particles 2000"
RUN="python2 run.py $COMMON_OPTIONS"
DEST_DIR=results/

mkdir -p "$DEST_DIR"

child_block() {
    # Will block until the process has less than the number of CPUs + 1 child
    # processes
    max="`expr $(nproc) + 1`"
    while [ "$(ps --ppid=$$ --no-header | wc -l)" -gt "$max" ]; do
        sleep 1
    done
}

for id in {00..10}; do
    trajectory=data/kitti/map_trajectories/${id}.txt.bz2
    map=data/kitti/${id}.osm.bz2
    echo "Spawning processes for trajectory $id"
    child_block
    $RUN --enablemapfilter --out "$DEST_DIR/${id}-map.csv" "$trajectory" "$map" &
    child_block
    $RUN --enableplainfilter --out "$DEST_DIR/${id}-plain.csv" "$trajectory" "$map" &
    echo "Spawning for $id done"
    sleep 2
done

wait
