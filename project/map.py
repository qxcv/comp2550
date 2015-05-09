"""Functions and classes for manipulating OpenStreetMap data."""

import numpy as np

from imposm.parser import OSMParser

from settings import DEFAULT_LANE_WIDTH


# These are all the most important road types. Some types have been ommitted in
# the interests of localisation effectiveness. See
# https://wiki.openstreetmap.org/wiki/Key:highway for more information
ROAD_TYPES = frozenset(
    ["motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link",
     "trunk_link", "primary_link", "secondary_link", "tertiary_link",
     "living_street", "road", "unclassified", "residential", "service"]
)


def perp(begin, end):
    """Return a 2D unit vector orthogonal to the line defined by the two 2D
    vectors begin and end"""
    proj_matrix = np.array([[0, -1], [1, 0]])
    delta = end - begin
    return np.dot(proj_matrix, delta) / np.linalg.norm(delta)


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
            # First, estimate the number of lanes
            num_lanes = 2
            tags = self._way_tags[way_id]

            if tags.get('oneway', None) == 'yes':
                num_lanes = 1

            if 'lanes' in tags:
                num_lanes = max(1, int(tags['lanes']))

            # Next, estimate lane width
            lane_width = DEFAULT_LANE_WIDTH
            # TODO

            # Join each pair of refs into a segment
            for begin_ref, end_ref in zip(refs, refs[1:]):
                begin = self._node_loc[begin_ref]
                end = self._node_loc[end_ref]
                proj_begin = projector(begin)
                proj_end = projector(end)

                orth = perp(proj_begin, proj_end)
                midpoint = (proj_begin, proj_end)

                lanes = []
                # Half the distance between the outmost lane centrelines
                all_offset = -1 * (num_lanes - 1) * lane_width / 2.0
                for i in xrange(num_lanes):
                    offset = all_offset + i * lane_width
                    lanes.append(midpoint + orth * offset)

                for lane in lanes:
                    self.segments.append(lane)

        # Finally, convert the segment beginnings and endings into some big
        # Numpy arrays
        self.begin_arr = np.array([b for b, e in self.segments])
        self.end_arr = np.array([e for b, e in self.segments])
        assert self.begin_arr.shape == self.end_arr.shape
        assert self.begin_arr.shape == (len(self.segments), 2)

    def _handle_ways(self, ways):
        rejected = set()
        for id, tags, refs in ways:
            if not refs or 'highway' not in tags:
                continue

            if tags['highway'] not in ROAD_TYPES:
                rejected.add(tags['highway'])
                continue

            self._way_refs[id] = refs
            self._way_tags[id] = tags

    def _handle_coords(self, coords):
        for coord in coords:
            # Yes, imposm.parser gives us coordinates in (lon, lat) format. I
            # don't know why.
            id, lon, lat = coord
            self._node_loc[id] = (lat, lon)

    def nearest_segment(self, point):
        pass
