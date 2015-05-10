"""Classes and utilities for illustrating particle filters."""

from math import cos, sin, sqrt, pi

from matplotlib import patches, transforms, pyplot as plt

# Base particle radius, metres
PARTICLE_RAD = 1


def mpl_draw_map(map, region=None):
    for begin, end in map.segments:
        plt.plot((begin[0], end[0]), (begin[1], end[1]), 'b-')


def plot_vehicle_tri(coords, yaw, color=(0, 0, 1, 0.5), zorder=None):
    """Plot a marker representing a vehicle (either ground truth or
    estimate)"""
    vertices = [
        [0, 0],
        [0.77, -0.5],
        [0, 0.5],
        [-0.77, -0.5]
    ]
    tri = patches.Polygon(
        vertices, closed=True, facecolor=color, edgecolor=(0, 0, 0),
        zorder=zorder
    )
    ax = plt.gca()
    tri.set_transform(transforms.Affine2D()
                                .scale(10)
                                .rotate(yaw - pi/2)
                                .translate(*coords)
                      + ax.transData)
    return ax.add_patch(tri)


class MapDisplay(object):
    """Class to display a fixed map with a set of points which move every so
    often."""

    TRUTH_Z_ORDER = 20
    ESTIMATE_Z_ORDER = 10
    CIRCLES_Z_ORDER = 0

    def __init__(self, map):
        self.map = map
        plt.ion()
        plt.gca().set_aspect('equal', 'datalim')
        mpl_draw_map(map)
        self.have_shown = False

        # Junk will be cleaned up when new points are drawn
        self.filter_junk = []
        self.gt_junk = None
        self.last_fix_junk = None

    def update_filter(self, filter):
        for junk in self.filter_junk:
            if isinstance(junk, list):
                for subjunk in junk:
                    subjunk.remove()
            else:
                junk.remove()

        self.filter_junk = []
        zorder = self.CIRCLES_Z_ORDER
        for i in xrange(filter.num_points):
            coords = filter.coords[i]
            weight = filter.weights[i]
            yaw = filter.yaws[i]

            # Significance of sqrt is that it makes circle areas proportional
            # to weight
            radius = PARTICLE_RAD * sqrt(
                weight * filter.num_points
            )

            # Draw the circle itself
            circ = patches.Circle(
                coords, radius, facecolor=(1, 0, 0, 0.2),
                edgecolor=(1, 0, 0, 0.8), zorder=zorder
            )

            # Draw the line in the center
            line_end = (
                coords[0] + radius*cos(yaw), coords[1] + radius*sin(yaw)
            )
            line_handle = plt.plot(
                (coords[0], line_end[0]), (coords[1], line_end[1]),
                color=(0, 0, 0, 0.8), zorder=zorder
            )
            plt.gca().add_patch(circ)

            # Add junk to be cleaned up next time
            self.filter_junk.append(line_handle)
            self.filter_junk.append(circ)

            zorder -= 1

        pred_x, pred_y, pred_yaw = filter.state_estimate()
        vehicle = plot_vehicle_tri(
            (pred_x, pred_y), pred_yaw, zorder=self.ESTIMATE_Z_ORDER
        )
        self.filter_junk.append(vehicle)

    def update_ground_truth(self, pos, yaw):
        if self.gt_junk is not None:
            self.gt_junk.remove()
        self.gt_junk = plot_vehicle_tri(
            pos, yaw, (0, 1, 0, 0.8), zorder=self.TRUTH_Z_ORDER
        )

    def update_last_fix(self, pos):
        if self.last_fix_junk is not None:
            for junk in self.last_fix_junk:
                junk.remove()
        self.last_fix_junk = plt.plot(
            pos[0], pos[1], marker='x', color='r', markersize=50
        )

    def redraw(self):
        plt.gca().set_aspect('equal', 'datalim')
        if not self.have_shown:
            plt.gcf().canvas.set_window_title('Map viewer')
            plt.show()
            self.have_shown = True
        else:
            plt.draw()
