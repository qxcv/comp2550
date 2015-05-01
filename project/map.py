"""Functions and classes for manipulating OpenStreetMap data."""

import numpy as np

from imposm.parser import OSMParser


# These are all the most important road types. There is also 'unclassified',
# 'residential' and some others. However, these have been ommitted in the
# interests of localisation effectiveness. See
# https://wiki.openstreetmap.org/wiki/Key:highway for more information
ROAD_TYPES = frozenset(
    ["motorway", "trunk", "primary", "secondary", "tertiary" "motorway_link",
     "trunk_link", "primary_link", "secondary_link", "tertiary_link",
     "living_street", "road", "unclassified", "residential"]
)


class Map(object):
    """Class representing all of the roads in an OpenStreetMap map."""
    def __init__(self, path, projector):
        """Takes a path to an OpenStreetMap map (tested with XML format) and
        initialises a Map instance containing all of the data therein.
        Projector will be a function to project (lat, lon) coordinates into
        something more tractable."""
        self.segments = []
        self._node_loc = {}
        self._way_refs = {}
        self._way_tags = {}
        p = OSMParser(
            coords_callback=self._handle_coords,
            ways_callback=self._handle_ways
        )
        p.parse(path)

        # Now we can resolve these into segments
        for way_id, refs in self._way_refs.iteritems():
            # Join each pair of refs into a segment
            for begin_ref, end_ref in zip(refs, refs[1:]):
                # Swap elements in both begin and end so that they're in (lat,
                # lon) format, then convert into Cartesian format
                begin = self._node_loc[begin_ref]
                end = self._node_loc[end_ref]
                proj_begin = projector((begin[1], begin[0]))
                proj_end = projector((end[1], end[0]))
                self.segments.append((proj_begin, proj_end))

        # Finally, convert the segment beginnings and endings into some big
        # Numpy arrays
        self.begin_arr = np.array([b for b, e in self.segments])
        self.end_arr = np.array([e for b, e in self.segments])
        assert self.begin_arr.shape == self.end_arr.shape
        assert self.begin_arr.shape == (len(self.segments), 2)

    def _handle_ways(self, ways):
        for id, tags, refs in ways:
            if not refs or 'highway' not in tags:
                continue

            if tags['highway'] not in ROAD_TYPES:
                continue

            self._way_refs[id] = refs
            self._way_tags[id] = tags

    def _handle_coords(self, coords):
        for coord in coords:
            # Yes, (lon, lat) is what it says on the imposm.parser page
            id, lon, lat = coord
            self._node_loc[id] = (lat, lon)
