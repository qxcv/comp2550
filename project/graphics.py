"""Classes and utilities for illustrating particle filters."""

from math import cos, sin, sqrt, pi

from matplotlib import patches, transforms

import numpy as np

# Base particle radius, metres
PARTICLE_RAD = 1


def mpl_draw_map(ax, map, region=None):
    for begin, end in map.segments:
        ax.plot((begin[0], end[0]), (begin[1], end[1]), 'b-')


def plot_vehicle_tri(ax, coords, yaw, color=(0, 0, 1, 0.5), zorder=None):
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
    tri.set_transform(transforms.Affine2D()
                                .scale(10)
                                .rotate(yaw - pi/2)
                                .translate(*coords)
                      + ax.transData)
    return ax.add_patch(tri)


def plot_vehicle_square(ax, coords, color=(0, 1, 0, 0.5), zorder=None):
    # It will be a side_length * side_length square
    side_length = 8
    # Unit rectangle at the origin
    rect = patches.Rectangle(
        (-0.5, -0.5), 1, 1, facecolor=color
    )
    rect.set_transform(transforms.Affine2D()
                                 .scale(side_length)
                                 .translate(*coords)
                       + ax.transData)
    return ax.add_patch(rect)


class MapDisplay(object):
    """Class to display a fixed map with a set of points which move every so
    often."""

    TRUTH_Z_ORDER = 20
    ESTIMATE_Z_ORDER = 10
    CIRCLES_Z_ORDER = 0

    def __init__(self, ax, map, smooth_zoom_rate=None, auto_focus=False,
                 auto_scale_rate=None):
        self.ax = ax
        self.map = map
        ax.set_aspect('equal', 'datalim')
        mpl_draw_map(ax, map)
        self.auto_focus = auto_focus
        self.auto_scale_rate = auto_scale_rate

        # Junk will be cleaned up when new points are drawn
        self.filter_junk = []
        self.gt_junk = None
        self.last_fix_junk = None

    def draw_filter(self, f):
        rv = []
        zorder = self.CIRCLES_Z_ORDER

        # These are used for auto-scaling (if enabled)
        min_x = min_y = -5
        max_x = max_y = 5

        for i in xrange(f.num_points):
            coords = f.coords[i]
            weight = f.weights[i]
            yaw = f.yaws[i]

            # Update maxima
            min_x = min(coords[0], min_x)
            min_y = min(coords[1], min_y)
            max_x = max(coords[0], max_x)
            max_y = max(coords[1], max_y)

            # Significance of sqrt is that it makes circle areas proportional
            # to weight
            radius = PARTICLE_RAD * sqrt(
                weight * f.num_points
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
            line_handle = self.ax.plot(
                (coords[0], line_end[0]), (coords[1], line_end[1]),
                color=(0, 0, 0, 0.8), zorder=zorder
            )
            self.ax.add_patch(circ)

            # Add junk to be cleaned up next time
            rv.append(line_handle)
            rv.append(circ)

            zorder -= 1

        pred_x, pred_y, pred_yaw = f.state_estimate()
        vehicle = plot_vehicle_tri(
            self.ax, (pred_x, pred_y), pred_yaw, zorder=self.ESTIMATE_Z_ORDER
        )
        rv.append(vehicle)

        # TODO
        if self.auto_scale_rate is not None:
            self.auto_scale(min_x, max_x, min_y, max_y)

        # Return all the junk we generated
        return rv

    def update_filters(self, filters):
        for junk in self.filter_junk:
            if isinstance(junk, list):
                for subjunk in junk:
                    subjunk.remove()
            else:
                junk.remove()

        self.filter_junk = []
        for f in filters:
            self.filter_junk.extend(self.draw_filter(f))

    def update_ground_truth(self, pos, yaw=None):
        if self.gt_junk is not None:
            self.gt_junk.remove()
        if yaw is None:
            self.gt_junk = plot_vehicle_square(
                self.ax, pos, (0, 1, 0, 0.8), zorder=self.TRUTH_Z_ORDER
            )
        else:
            self.gt_junk = plot_vehicle_tri(
                self.ax, pos, yaw, (0, 1, 0, 0.8), zorder=self.TRUTH_Z_ORDER
            )
        if self.auto_focus:
            self.focus_on(*pos)

    def update_last_fix(self, pos):
        if self.last_fix_junk is not None:
            for junk in self.last_fix_junk:
                junk.remove()
        self.last_fix_junk = self.ax.plot(
            pos[0], pos[1], marker='x', color='r', markersize=50
        )

    def focus_on(self, cx, cy):
        """Center the axes on (cx, cy) whilst retaining scale"""
        current_xlim = np.array(self.ax.get_xlim())
        current_ylim = np.array(self.ax.get_ylim())
        new_xlim = current_xlim - np.mean(current_xlim) + cx
        new_ylim = current_ylim - np.mean(current_ylim) + cy
        self.set_xlim(*new_xlim)
        self.set_ylim(*new_ylim)

    def auto_scale(self, xmin, xmax, ymin, ymax):
        """Zoom in or out the axes until the bounding box specified by
        {x,y}{min,max} is in view"""
        target_limits = np.array([[xmin, xmax], [ymin, ymax]])
        current_limits = np.array([
            self.ax.get_xlim(),
            self.ax.get_ylim()
        ])

        # Where are we focused at the moment?
        current_focus = np.mean(current_limits, axis=1).reshape((2, 1))
        shifted_targets = target_limits - current_focus

        # new 1/2 width and new 1/2 height
        x_span, y_span = np.amax(np.abs(shifted_targets), axis=1)

        # Now set bounding boxes
        x_mean, y_mean = current_focus
        np.xlim(x_mean - x_span, x_mean + x_span)
        np.ylim(x_mean - x_span, y_mean + y_span)

    def redraw(self):
        self.ax.set_aspect('equal', 'datalim')
