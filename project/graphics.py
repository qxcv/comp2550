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
    update_vehicle_tri(ax, tri, coords, yaw)
    return ax.add_patch(tri)


def update_vehicle_tri(ax, patch, coords, yaw):
    """Update transform for an existing vehicle triangle patch. Faster than
    removing the patch and drawing it again."""
    patch.set_transform(transforms.Affine2D()
                                  .scale(10)
                                  .rotate(yaw - pi/2)
                                  .translate(*coords)
                        + ax.transData)
    return patch


def plot_vehicle_square(ax, coords, color=(0, 1, 0, 0.5), zorder=None):
    # Unit rectangle at the origin, scaled later
    rect = patches.Rectangle(
        (-0.5, -0.5), 1, 1, facecolor=color
    )
    update_vehicle_square(ax, rect, coords)
    return ax.add_patch(rect)


def update_vehicle_square(ax, patch, coords):
    patch.set_transform(transforms.Affine2D()
                                  .scale(8)
                                  .translate(*coords)
                        + ax.transData)
    return patch


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
        self.gt_patch = None
        self.last_fix_data = None
        self.estimate_patch = None
        self.circles = []
        self.lines = []

    def draw_filter(self, f):
        zorder = self.CIRCLES_Z_ORDER

        # These are used for auto-scaling (if enabled)
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

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

            # assert len(self.circles) == len(self.lines)

            # Draw the circle itself
            circ_trn = transforms.Affine2D() \
                                 .scale(radius) \
                                 .translate(*coords) \
                + self.ax.transData
            if i >= len(self.circles):
                circ = patches.Circle(
                    (0, 0), 1, facecolor=(1, 0, 0, 0.2),
                    edgecolor=(1, 0, 0, 0.8), zorder=zorder
                )
                self.circles.append(circ)
                self.ax.add_patch(circ)
            else:
                circ = self.circles[i]
            circ.set_transform(circ_trn)

            # Draw the line in the center
            line_end = (
                coords[0] + radius*cos(yaw), coords[1] + radius*sin(yaw)
            )
            line_data = (
                (coords[0], line_end[0]), (coords[1], line_end[1])
            )
            if i >= len(self.lines):
                line_handle, = self.ax.plot(
                    *line_data, color=(0, 0, 0, 0.8), zorder=zorder
                )
                self.lines.append(line_handle)
            else:
                line_handle = self.lines[i]
                line_handle.set_data(*line_data)

            zorder -= 1

        pred_x, pred_y, pred_yaw = f.state_estimate()
        if self.estimate_patch is None:
            self.estimate_patch = plot_vehicle_tri(
                self.ax, (pred_x, pred_y), pred_yaw,
                zorder=self.ESTIMATE_Z_ORDER
            )
        else:
            update_vehicle_tri(
                self.ax, self.estimate_patch, (pred_x, pred_y), pred_yaw
            )

        if self.auto_scale_rate is not None:
            self.auto_scale(min_x, max_x, min_y, max_y)

    def update_filters(self, filters):
        for f in filters:
            self.draw_filter(f)

    def update_ground_truth(self, pos, yaw=None):
        if self.gt_patch is not None:
            if yaw is None:
                update_vehicle_square(self.ax, self.gt_patch, pos)
            else:
                update_vehicle_tri(self.ax, self.gt_patch, pos, yaw)
        else:
            if yaw is None:
                self.gt_patch = plot_vehicle_square(
                    self.ax, pos, (0, 1, 0, 0.8),
                    zorder=self.TRUTH_Z_ORDER
                )
            else:
                self.gt_patch = plot_vehicle_tri(
                    self.ax, pos, yaw, (0, 1, 0, 0.8),
                    zorder=self.TRUTH_Z_ORDER
                )
        if self.auto_focus:
            self.focus_on(*pos)

    def update_last_fix(self, pos):
        if self.last_fix_data is None:
            self.last_fix_data, = self.ax.plot(
                *pos, marker='x', color='r', markersize=50
            )
        else:
            self.last_fix_data.set_data(*pos)

    def focus_on(self, cx, cy):
        """Center the axes on (cx, cy) whilst retaining scale"""
        current_xlim = np.array(self.ax.get_xlim())
        current_ylim = np.array(self.ax.get_ylim())
        new_xlim = current_xlim - np.mean(current_xlim) + cx
        new_ylim = current_ylim - np.mean(current_ylim) + cy
        self.ax.set_xlim(*new_xlim)
        self.ax.set_ylim(*new_ylim)

    def auto_scale(self, xmin, xmax, ymin, ymax):
        """Zoom in or out the axes until the bounding box specified by
        {x,y}{min,max} is in view"""
        # TODO: Actually use self.auto_scale_rate
        target_limits = np.array([[xmin, xmax], [ymin, ymax]])
        current_limits = np.array([
            self.ax.get_xlim(),
            self.ax.get_ylim()
        ])

        # Where are we focused at the moment?
        current_focus = np.mean(current_limits, axis=1).reshape((2, 1))
        shifted_targets = target_limits - current_focus

        # new 1/2 width and new 1/2 height
        x_span, y_span = np.abs(shifted_targets).max(axis=1)
        x_span = max(100, x_span)
        y_span = max(100, y_span)

        # Now set bounding boxes
        x_mean, y_mean = current_focus
        self.ax.set_xlim(x_mean - x_span, x_mean + x_span)
        self.ax.set_ylim(y_mean - y_span, y_mean + y_span)

    def redraw(self):
        self.ax.set_aspect('equal', 'datalim')
