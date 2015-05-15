#!/usr/bin/env python

from json import dumps
from sys import stdin

if __name__ == '__main__':
    coords = []
    for line in stdin:
        lat, lon = map(float, line.split()[:2])
        coords.append([lon, lat]) # yep, GeoJSON does it differently
    output_dict = {
        "type": "LineString",
        "coordinates": coords
    }
    print(dumps(output_dict))
