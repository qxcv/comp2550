"""Noise models for common vehicle sensors."""

from copy import deepcopy

import numpy as np


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


def noisify(obs_gen, gps_stddev, speed_noise, gyro_stddev):
    """Applies GPS, gyroscope and speedometer noise to the given observation
    sequence. Yields (ground truth, noisy observation) pairs."""
    assert 1 >= speed_noise >= 0
    assert gyro_stddev >= 0
    assert gps_stddev >= 0

    # Emulates a miscalibrated speedometer. At most +-2.5km/h of error at
    # 100km/h
    speedo_multiplier = 1 + np.random.uniform(-speed_noise, speed_noise)

    for obs in obs_gen:
        new_obs = deepcopy(obs)

        # Add GPS noise. This is not a very good emulation, because it grows
        # without bound, but it will have to do for now (why implement
        # something more complicated when you have NFI what GPS noise actually
        # looks like?).
        new_obs.pos = np.random.multivariate_normal(
            obs.pos, gps_stddev**2 * np.eye(2)
        )

        # Add gyro noise. I got this formula out of thin air BECAUSE NOBODY
        # CARES ABOUT PRECISE NOISE MODELS. Anyway, this will keep 95% of
        # measurements within 5% of their true values.
        if 'wu' in new_obs:
            new_obs['wu'] += np.random.normal(0, gyro_stddev)

        # Add speedometer noise
        if 'vf' in new_obs:
            new_obs['vf'] *= speedo_multiplier

        # Yield the ground truth and its noisy counterpart
        yield obs, new_obs
