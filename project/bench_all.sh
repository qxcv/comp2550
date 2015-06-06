#!/bin/bash

# Run over all of the given examples and produce some nice CSVs

COMMON_OPTIONS="--particles 2000"
RUN="python2 run.py $COMMON_OPTIONS"
DEST_DIR=results/
MANGLE="python2 mangle_data.py"

mkdir -p "$DEST_DIR"

child_block() {
    # Will block until the process has less than the number of CPUs + 1 child
    # processes
    max="`expr $(nproc) + 1`"
    while [ "$(ps --ppid=$$ --no-header | wc -l)" -gt "$max" ]; do
        sleep 1
    done
}

scrape() {
    # Scrape generated CSVs to produce something that can be thrown in the
    # final report
    for id in {00..10}; do
        prefix="$DEST_DIR/${id}"
        $MANGLE --mapfilter "$prefix-map.csv"
        $MANGLE --plainfilter "$prefix-plain.csv"
    done
}

case $1 in
    scrape)
        scrape
        ;;
    *)
        echo "Writing CSVs"
        for id in {00..10}; do
            trajectory=data/kitti/map_trajectories/${id}.txt.bz2
            map=data/kitti/${id}.osm.bz2
            echo "Spawning processes for trajectory $id"
            child_block
            $RUN --enablemapfilter --out "$DEST_DIR/${id}-map.csv" \
                "$trajectory" "$map" &
            child_block
            $RUN --enableplainfilter --out "$DEST_DIR/${id}-plain.csv" \
                "$trajectory" "$map" &
            echo "Spawning for $id done"
            sleep 2
        done

        wait
        scrape
        ;;
esac

