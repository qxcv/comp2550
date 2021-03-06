#!/bin/sh

# Produces a visual comparison between a map-based particle filter and a plain
# particle filter using Jose's data

TIMES="0.1 4.6 9.2 12.4 14.4 16.8"

die() {
    echo $@
    exit 1
}

writevids() {
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
}

splicevids() {
    if [ -z "$1" ]; then
        echo "Need a video to splice"
        exit 1
    fi
    mkdir -p report/spliced || die "mkdir failed"
    for time in $TIMES; do
        echo Splicing at "$time"
        dest="report/spliced/$1-${time}.png"
        ffmpeg -y -i "$1" -ss "$time" -vframes 1 "$dest" || die "FFmpeg failed"
        convert "$dest" -shave 90x50 "$dest"
    done
}

case $1 in
    write)
        writevids
        ;;
    splice)
        shift
        splicevids $@
        ;;
    *)
        echo "USAGE: $0 <command> <arguments>"
        echo "Commands:"
        echo "   write"
        echo "   splice <video>"
        exit 1
        ;;
esac
