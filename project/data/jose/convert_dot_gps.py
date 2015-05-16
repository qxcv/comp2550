#!/usr/bin/env python3

"""This program converts a collection of .gps files to a simple CSV format"""

import re

from csv import DictWriter
from datetime import datetime
from glob import glob
from os.path import join, basename
from sys import argv, stdout
from time import mktime

TIMESTAMP_RE = re.compile(
    r'^test_'
    r'(?P<year>\d{4})'
    r'(?P<month>\d{2})'
    r'(?P<day>\d{2})'
    r'(?P<hour>\d{2})'
    r'(?P<minute>\d{2})'
    r'(?P<second>\d{2})'
    r'_'
    r'(?P<millisecond>\d{3})'
    r'.gps$'
)

if __name__ == '__main__':
    # The .gps files are weird. They each seem to consist of a single line
    # containing five numbers. My guess is that these are latitude, longitude,
    # altitude, something to do with whether the signal was actually received
    # (maybe it's 0 if we're in a tunnel?) and some junk number which doesn't
    # change throughout the entire sequence.
    directory, = argv[1:]
    paths = glob(join(directory, 'test_*.gps'))
    samples = []
    for path in sorted(paths):
        # The file names are of the form
        # test_<year><month><day><h><m><s>_<ms>.gps. This means that the
        # ascending lexicographic sort should have put them in the right order.
        with open(path) as fp:
            contents = fp.read().split()

        groups = TIMESTAMP_RE.match(basename(path)).groupdict()

        dt = datetime(
            year=int(groups['year']),
            month=int(groups['month']),
            day=int(groups['day']),
            hour=int(groups['hour']),
            minute=int(groups['minute']),
            second=int(groups['second']),
        )

        # Floating point unix time
        timestamp = mktime(dt.utctimetuple()) \
            + float(groups['millisecond']) / 1000

        samples.append({
            'time': timestamp,
            'latitude': float(contents[0]),
            'longitude': float(contents[1]),
            'altitude': float(contents[2]),
            'signal': True if int(contents[3]) == 1 else False,
            # No idea what the last field is
            'junk': int(contents[4])
        })

    csv_writer = DictWriter(stdout, ('time', 'lat', 'lon', 'signal'))
    csv_writer.writeheader()

    init_timestamp = None

    for sample in samples:
        if init_timestamp is None:
            init_timestamp = sample['time']
        t = sample['time'] - init_timestamp
        csv_writer.writerow({
            'time': t,
            'lat': sample['latitude'],
            'lon': sample['longitude'],
            'signal': sample['signal']
        })

    stdout.flush()
