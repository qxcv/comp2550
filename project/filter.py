"""Particle filter implementation."""

import numpy as np


class ParticleFilter(object):
    def __init__(self, num_points, init_coords, init_sigma):
        self.num_points = num_points

        # Particles are initialised using an isotropic Gaussian with covariance
        # matrix init_stddev * I and mean given by init_coords. Remember that
        # the matrix is stored with one (x, y) coordinate per row and
        # num_points rows.
        self.coords = np.random.multivariate_normal(
            init_coords, init_sigma * np.eye(2), num_points
        )

        # Particle yaws are initialised randomly in [0, 2*pi]
        self.yaws = np.random.uniform(0, 2*np.pi, num_points)

        # Particle weights are initially uniform
        self.weights = np.ones(num_points) / num_points

    def normalise_weights(self):
        """Ensure that weights sum to one."""
        self.weights = self.weights / np.sum(self.weights)

    def effective_particles(self):
        # Filter should resample when this quantity falls below some threshold,
        # which Gustaffson et al. (2002) recommend be set to 2N/3
        return 1.0 / np.sum(np.square(self.weights))

    def auto_resample(self):
        """Resample iff the number of effective particles drops below two
        thirds of ``self.num_points``"""
        if self.effective_particles() < 2.0 / 3.0 * self.num_points:
            self.resample()

    def resample(self):
        """Draw ``self.num_points`` samples from distribution given by current
        particle weights."""
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
        """Give a best estimate for the current state of the vehicle."""
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
        mean_yaw = np.arctan2(mean_y, mean_x).reshape((1,))

        return np.concatenate((coords, mean_yaw))

    def measure_gps(self, mean, stddev):
        """Measure a GPS-like sensor reading with Cartesian coordinates given
        by ``mean`` and uncertainty represented by an isotropic Gaussian with
        standard deviation ``stddev``"""
        precision = np.eye(2) / stddev
        diffs = self.coords - mean
        by_precision = np.dot(precision, diffs.T).T
        # We don't need to normalise, so these aren't exactly Gaussians
        likelihoods = np.exp(-0.5 * np.einsum('ij,ij->i', diffs, by_precision))
        assert likelihoods.shape == (self.num_points,), likelihoods.shape
        self.weights *= likelihoods

    def measure_map(self, map):
        for idx, point in enumerate(self.coords):
            pass

    def predict(self, dt, forward_speed, yaw_diff):
        # TODO:
        #  1) Normalise yaws to be in (0, 2 * pi)
        #  2) REALISTIC noise model is needed!
        #  3) Incorporate delta-t so that noise is delta-time-dependent
        noisy_yaws = np.random.normal(
            yaw_diff, 0.25, (self.num_points,)
        )
        self.yaws += dt * noisy_yaws
        noisy_odom = dt * (forward_speed + np.random.uniform(
            -0.5, 1, (self.num_points,)
        ))
        self.coords[:, 0] += noisy_odom * np.cos(self.yaws)
        self.coords[:, 1] += noisy_odom * np.sin(self.yaws)
