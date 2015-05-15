"""Functions and classes for manipulating OpenStreetMap data."""

import numpy as np

from imposm.parser import OSMParser

from CGAL.CGAL_AABB_tree import AABB_tree_Segment_3_soup
from CGAL.CGAL_Kernel import Segment_3, Point_3

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
            # TODO: More accurate estimates

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

        seg3ds = []
        for begin, end in self.segments:
            p1 = Point_3(*(list(begin) + [0]))
            p2 = Point_3(*(list(end) + [0]))
            seg = Segment_3(p1, p2)
            seg3ds.append(seg)

        self._aabb_tree = AABB_tree_Segment_3_soup(seg3ds)
        assert self._aabb_tree.accelerate_distance_queries()

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

    def nearest_lane_dist(self, point):
        x, y = point
        p = Point_3(x, y, 0)
        nearest = self._aabb_tree.closest_point(p)
        return np.sqrt((x - nearest.x())**2 + (y - nearest.y())**2)


def JoseMap(Map):
    """Map subclass dedicated to loading Jose's GPS trace maps"""
    def __init__(self, path, projector):
        pass
