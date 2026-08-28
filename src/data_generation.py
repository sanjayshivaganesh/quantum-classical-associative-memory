"""Random bipolar patterns and input-corruption utilities."""

import numpy as np


def random_bipolar_patterns(n_patterns, n_bits, rng=None):
    """Draw ``n_patterns`` independent random ±1 patterns of length ``n_bits``."""
    if rng is None:
        rng = np.random
    return rng.choice([-1, 1], size=(n_patterns, n_bits))


def corrupt_bernoulli(pattern, rate, rng=None):
    """Flip each bit independently with probability ``rate``.

    Used by the noise-robustness sweep, scaling, statistical-significance,
    and large-scale inference experiments.
    """
    if rng is None:
        rng = np.random
    corrupted = pattern.copy()
    mask = rng.rand(len(pattern)) < rate
    corrupted[mask] *= -1
    return corrupted


def corrupt_fixed_count(pattern, noise_level, rng=None):
    """Flip exactly ``max(1, int(len(pattern) * noise_level))`` bits.

    Used by the storage-capacity and circuit-depth experiments.
    At ``noise_level == 0`` this still flips one bit, matching the original
    experiment code.
    """
    if rng is None:
        rng = np.random
    corrupted = pattern.copy()
    n_flip = max(1, int(len(pattern) * noise_level))
    flip_idx = rng.choice(len(pattern), size=n_flip, replace=False)
    corrupted[flip_idx] *= -1
    return corrupted
