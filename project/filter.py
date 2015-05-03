"""Particle filter implementation."""

import numpy as np


class ParticleFilter(object):
    def __init__(self, num_points, init_coords, init_stddev):
        self.num_points = num_points

        # Particles are initialised using an isotropic Gaussian with covariance
        # matrix init_stddev * I and mean given by init_coords. Remember that
        # the matrix is stored with one coordinate per row and num_points rows.
        self.coords = np.random.multivariate_normal(
            init_coords, init_stddev * np.eye(2), num_points
        )

        # Particle yaws are initialised randomly in [0, 2*pi]
        self.yaws = np.random.uniform(0, 2*np.pi, num_points)

        # Particle weights are initially uniform
        self.weights = np.ones(num_points) / num_points

    def normalise_weights(self):
        self.weights = self.weights / np.sum(self.weights)

    def effective_particles(self):
        # Filter should resample when this quantity falls below some threshold,
        # which Gustaffson et al. (2002) recommend be set to 2N/3
        return 1.0 / np.sum(np.square(self.weights))

    def resample(self):
        self.normalise_weights()

        # Produce a vector of indices into our coordinate, yaw and weights
        # vectors, choosing according the the probability distribution defined
        # by our current weights
        samples = np.random.choice(
            np.arange(self.num_points),
            size=self.num_points,
            p=self.weights
        )

        # Now resample from our set of particles
        self.coords = self.coords[samples]
        self.yaws = self.yaws[samples]

        # Set weights to be uniform
        self.weights = np.ones(self.num_points) / self.num_points

    def state_estimate(self):
        # State estimate is simply weighted sum of particle states
        self.normalise_weights()
        coords = np.dot(self.weights, self.coords).reshape((2,))

        # Angular means are tricky. Here we convert all of the yaws to unit
        # vectors, then add the unit vectors together to come up with a
        # weighted mean vector, which can then be converted to an angle.
        yaw_xs = np.cos(self.yaws)
        yaw_ys = np.sin(self.yaws)
        mean_x = np.dot(self.weights, yaw_xs)
        mean_y = np.dot(self.weights, yaw_ys)
        mean_yaw = np.arctan2(mean_y, mean_x).reshape((1,)) + np.pi

        return np.concatenate((coords, mean_yaw))
