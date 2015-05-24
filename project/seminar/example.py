#!/usr/bin/env python2

"""Example of 1D particle filtering for localisation"""

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.image as mimg
import matplotlib.transforms as mtrn
import numpy as np

INITIAL_POSITION = 0
FINAL_POSITION = 1
X_BOUNDS = [-2, 3]
NUM_PARTICLES = 250
PLOT_HEIGHT = 4
POS_SIGMA = 0.2


def plot_scenario(location, particles, heights, norm_params=None):
    # Measurement
    if norm_params is not None:
        points = np.linspace(X_BOUNDS[0], X_BOUNDS[1], 1000)
        plt.plot(
            points, mlab.normpdf(points, *norm_params)+0.1, color='g', lw='3'
        )

    # Particles
    plt.scatter(particles, heights, marker='o', color=(0, 0, 0))

    # Robot
    robot = mimg.imread('images/robot.png')
    robot_width = 0.25
    robot_height = robot_width * float(robot.shape[0]) / robot.shape[1]
    x_width = X_BOUNDS[1] - X_BOUNDS[0]
    robot_loc = [
        (location - X_BOUNDS[0]) / float(x_width) - robot_width / 2,
        0, robot_width, robot_height
    ]
    bounds = mtrn.Bbox.from_bounds(*robot_loc)
    transformed = mtrn.TransformedBbox(bounds, plt.gca().transAxes)
    bb = mimg.BboxImage(
        transformed,
        norm=None,
        origin=None,
        clip_on=True
    )
    bb.set_data(robot)
    bb.set_zorder(10)
    plt.gca().add_artist(bb)

    # Bounds
    plt.ylim(ymin=0, ymax=PLOT_HEIGHT)
    plt.xlim(*X_BOUNDS)


def save(idx):
    plt.axis('off')
    plt.savefig(
        'images/pf-{}.png'.format(idx), bbox_inches='tight', pad_inches=0
    )
    plt.clf()

if __name__ == '__main__':
    # Initial distribution
    particles = np.random.normal(0, 0.5, size=NUM_PARTICLES)
    heights = np.random.normal(
        2 * PLOT_HEIGHT/3.0, PLOT_HEIGHT/16.0, size=NUM_PARTICLES
    )
    plot_scenario(INITIAL_POSITION, particles, heights)
    save(1)

    # Move
    plot_scenario(FINAL_POSITION, particles, heights)
    save(2)

    # Predict
    movement = FINAL_POSITION - INITIAL_POSITION
    particles += np.random.normal(movement, 0.6, size=NUM_PARTICLES)
    plot_scenario(FINAL_POSITION, particles, heights)
    save(3)

    # Measure
    measurement_location = np.random.normal(FINAL_POSITION, POS_SIGMA)
    plot_scenario(
        FINAL_POSITION, particles, heights, (measurement_location, POS_SIGMA)
    )
    save(4)

    # Update
    weights = mlab.normpdf(particles, measurement_location, POS_SIGMA)
    weights /= np.sum(weights)
    particles = np.random.choice(
        particles, p=weights, size=NUM_PARTICLES
    )
    plot_scenario(FINAL_POSITION, particles, heights)
    save(5)
