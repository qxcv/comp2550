"""Noise models for common vehicle sensors."""

import numpy as np


def white_gaussian(stddev=1, shape=None):
    """Yield white Gaussian noise with a given standard deviation and Numpy
    array shape (if None, values will be scalar)."""
    while True:
        yield np.random.normal(scale=stddev, size=shape)


def white_uniform(lower=0, upper=1, shape=None):
    """Yield uniform noise in [lower, upper] with given shape (or scalar if
    None)."""
    while True:
        yield np.random.uniform(lower, upper, shape)


def brownian(step_size=1, shape=None):
    """Yields a sequence of points with the given shape, each of which is one
    step_size step away from the previous one in a random direction (where
    direction is chosen uniformly)."""
    # See http://mathworld.wolfram.com/HyperspherePointPicking.html to
    # understand how we choose direction
    mean = np.zeros(shape)
    while True:
        yield mean
        gauss_vars = np.random.standard_normal(shape)
        direction = gauss_vars / np.sqrt(np.sum(gauss_vars ** 2))
        mean += step_size * direction


def noisy_gps_gen(observation_sequence):
    """Applies GPS-like noise to a series of observations."""
    random_walk_noise = brownian(0.1, shape=(2,))
    white_noise = white_gaussian(0.1, shape=(2,))
    for obs in observation_sequence:
        noise = next(random_walk_noise)
        noise += next(white_noise)
        # TODO


def noisy_gyroscope_gen(observation_sequence):
    pass


def noisy_odom_gen(observation_sequence):
    pass


def noisify(obs_gen):
    """Applies GPS-like, gyro-like and odom-like noise to the given observation
    sequence."""
    for obs in obs_gen:
        new_obs
