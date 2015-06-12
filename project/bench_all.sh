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
    max="`expr $(nproc) - 2`"
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

    script="`mktemp`"
    cat > "$script" <<PYTHON
from itertools import *
from sys import argv
from os.path import basename

import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

# Load data with Pandas
paths = argv[1].split('?:delim:?')[1:]
map_names = [basename(p).split('-')[0] for p in paths]
loaded = list(map(pd.read_csv, paths))
with_map = loaded[::2]
without_map = loaded[1::2]
map_hpe = [table['map_hpe'].as_matrix() for table in with_map]
plain_hpe = [table['plain_hpe'].as_matrix() for table in without_map]
all_hpes = list(chain.from_iterable(zip(map_hpe, plain_hpe)))

colours = (
    (0.161, 0.31, 0.427),
    (0.667, 0.475, 0.224)
)

# Make Matplotlib use Computer Modern for our PGF diagrams
matplotlib.rcParams.update({
    'font.family': 'serif',
    'pgf.rcfonts': False,
    'pgf.texsystem': 'pdflatex',
    'xtick.labelsize': 'x-small',
    'ytick.labelsize': 'x-small',
    'axes.labelsize': 'small'
})

# Now make a box chart showing horizontal positioning error
bp = plt.boxplot(all_hpes, sym='')

# Make everything BLACK
plt.setp(bp['boxes'], color='black')
plt.setp(bp['whiskers'], color='black')
plt.setp(bp['fliers'], color='black')

# Set y limit correctly so that we can use it later
plt.ylim(ymin=0, ymax=25)
y_min, y_max = plt.ylim()
top_offset = y_max - 0.04 * (y_max - y_min)

rects = []
for idx, box in enumerate(bp['boxes']):
    # Fill the box with the correct colour
    box.set_fillstyle('none')
    xdata = box.get_xdata()
    xstart = min(xdata)
    width = max(xdata) - xstart
    ydata = box.get_ydata()
    ystart = min(ydata)
    height = max(ydata) - ystart
    colour = colours[idx % len(colours)]
    r = Rectangle(
        (xstart, ystart), width, height, zorder=-1, fc=colour, ec='none'
    )
    plt.gca().add_patch(r)
    rects.append(r)

    # Add in a mean indicator
    hpe = all_hpes[idx]
    mean = '{:.2f}'.format(np.mean(hpe))
    plt.text(
        xstart + width / 2.0, top_offset, str(mean), ha='center', va='top',
        fontsize='x-small', rotation=90
    )

plt.xticks(np.arange(len(all_hpes))+1, map_names)
plt.legend(
    (rects[0], rects[1]), ('With map', 'Without map'), loc='upper right',
    bbox_to_anchor=(0.975, 0.85), fontsize='small'
)
plt.xlabel('Trace number')
plt.ylabel('HPE (m)')
plt.title('Particle filter horizontal positioning error')

# Remove redundant whitespace and fit plot to a single page
# TODO: Make the plot wider
plt.gcf().set_size_inches((5, 4))
plt.tight_layout()
plt.savefig('report/images/boxplot.pgf')
print("Success!")
PYTHON
python3 "$script" "$args" || echo "Python failed :("
rm "$script"
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

        wait
        scrape
        ;;
esac

