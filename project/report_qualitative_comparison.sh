#!/bin/sh

# Produces a visual comparison between a map-based particle filter and a plain
# particle filter using Jose's data

COMMON_OPTIONS="--codec huffyuv --particles 2000 --gpsstddev 0 --noimu --hidegt --jose data/jose/trace.csv data/jose/demo_GPS_ECCV_TUNEL.mat"

echo "Attempting with map filter"
CMD1="python2 run.py $COMMON_OPTIONS --enablemapfilter --movie with-map.avi"
echo "$CMD1"
$CMD1 &
echo "Attempting without map filter"
CMD2="python2 run.py $COMMON_OPTIONS --enableplainfilter --movie without-map.avi"
echo "$CMD2"
$CMD2 &
wait
echo "Both done!"
