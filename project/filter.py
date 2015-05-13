"""Particle filter implementation."""

import numpy as np


class ParticleFilter(object):
    def __init__(self, num_points, init_coords, init_sigma, have_imu=True):
        """Initialise num_points particles using an isotropic Gaussian with
        variance init_sigma and mean init_coords. If track_vel is True, the
        filter will store velocities as well as the headings and yaws which it
        tracks normally."""
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

        # Store speeds if necessary
        self.have_imu = have_imu
        if not have_imu:
            self.velocities = np.random.multivariate_normal(
                [0, 0], 5 * np.eye(2), num_points
            )

    def normalise_weights(self):
        """Ensure that weights sum to one."""
        self.weights = self.weights / np.sum(self.weights)

    def effective_particles(self):
        """Filter should resample when this quantity falls below some
        threshold, which Gustaffson et al. (2002) recommend be set to 2N/3"""
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
        # Force yaws to be in [0, 2pi)
        self.yaws %= 2 * np.pi

        if not self.have_imu:
            self.velocities = self.velocities[samples]

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

    def measure_map(self, m):
        """Incorporate measurements from the Map instance m using a Cauchy-like
        PDF over distances of each particle from their nearest road
        segments."""
        dists = np.zeros((self.num_points,))
        for idx, point in enumerate(self.coords):
            dists[idx] = m.nearest_lane_dist(point)
        factors = 1.0 / (1 + dists)
        self.weights *= factors

    def predict(self, dt, *args):
        """Update the particles according to the state transition model."""
        if self.have_imu:
            return self.predict_imu(dt, *args)
        return self.predict_no_imu(dt)

    def predict_imu(self, dt, forward_speed, yaw_diff):
        """Update particles if we have IMU data (and thus do not need to keep
        velocity or other higher dimensional data around)"""
        assert self.have_imu
        # TODO:
        #  1) REALISTIC noise model is needed! Can find this experimentally.
        noisy_yaws = np.random.normal(
            yaw_diff, 0.6, (self.num_points,)
        )
        # Don't worry about forcing yaws into [0, 2 * pi), since we'll do that
        # when we resample
        self.yaws += dt * noisy_yaws
        # We're using a Gaussian because it's easy to sample from and gives
        # values in (-inf, inf)
        odom_noisy = np.random.normal(
            forward_speed, abs(forward_speed) * 0.8, size=(self.num_points,)
        )
        noisy_odom = dt * odom_noisy
        self.coords[:, 0] += noisy_odom * np.cos(self.yaws)
        self.coords[:, 1] += noisy_odom * np.sin(self.yaws)

    def predict_no_imu(self, dt):
        # This transition Gaussian was fitted from the available map
        # trajectories. See investigate_transitions.py
        new_velocities = np.random.multivariate_normal(
            self.velocities, dt * 0.1 * np.eye(2)
        )
        self.coords += 0.5 * dt * (self.velocities + new_velocities)
        self.velocities = new_velocities

        # Keep yaws updated as well for the good of the visualisation code.
        # This can be disabled in "production"
        self.yaws = np.atan2(self.velocities[:, 1], self.velocities[:, 0])
        self.yaws %= 2 * np.pi
