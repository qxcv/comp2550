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
    args=""
    for id in {00..10}; do
        prefix="$DEST_DIR/${id}"
        args="$args?:delim:?$prefix-map.csv?:delim:?$prefix-plain.csv"
    done

python3 - "$args" <<EOF
from itertools import *
from sys import argv
from os.path import basename

import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

# Load data with Pandas
paths = argv[1].split('?:delim:?')[1:]
map_names = [basename(p).split('-')[0] for p in paths]
loaded = list(map(pd.read_csv, paths))
with_map = loaded[::2]
without_map = loaded[1::2]
map_hpe = [table['map_hpe'].as_matrix() for table in with_map]
plain_hpe = [table['plain_hpe'].as_matrix() for table in without_map]
all_hpes = list(chain.from_iterable(zip(map_hpe, plain_hpe)))

# Make Matplotlib use Computer Modern for our PGF diagrams
matplotlib.rcParams.update({
    'font.family': 'serif',
    'pgf.rcfonts': False,
    'pgf.texsystem': 'pdflatex'
})

# Now make a box chart showing horizontal positioning error
plt.boxplot(all_hpes)
plt.xticks(np.arange(len(all_hpes))+1, map_names)
plt.xlabel('Data set')
plt.ylabel('HPE (m)')
plt.title('Particle filter horizontal positioning error')
plt.ylim(ymax=100, ymin=0)

# Remove redundant whitespace and fit plot to a single page
plt.gcf().set_size_inches((7, 4))
plt.tight_layout()
plt.savefig('results/boxplot.png')
plt.savefig('results/boxplot.pgf')
print("Success!")
EOF

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

