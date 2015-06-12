#!/bin/bash

# See how long the algorithm takes with and without map information for
# different numbers of particles

PARTICLE_COUNTS=`echo {500..2000..500}`
RUN="python2 run.py"
DEST_DIR=results/

mkdir -p "$DEST_DIR"

for id in {00..10}; do
    echo "# Attempting times for trajectory $id"
    for particles in $PARTICLE_COUNTS; do
        echo "## With $particles particles"
        trajectory=data/kitti/map_trajectories/${id}.txt.bz2
        map=data/kitti/${id}.osm.bz2
        echo "### Spawning map filter"
        $RUN --enablemapfilter --particles $particles \
            "$trajectory" "$map"
        echo "### Spawning plain filter"
        $RUN --enableplainfilter --particles $particles \
            "$trajectory" "$map"
    done
    echo
    echo
done
