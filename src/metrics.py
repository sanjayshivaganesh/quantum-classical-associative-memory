"""Accuracy, confidence-interval, and effect-size helpers."""

import numpy as np
from scipy.stats import sem, t


def bit_accuracy(pred, true):
    """Fraction of matching bits."""
    return float(np.mean(pred == true))


def full_accuracy(pred, true):
    """1.0 if every bit matches, otherwise 0.0."""
    return float(np.all(pred == true))


def hamming_error(pred, true):
    """Fraction of mismatched bits."""
    return float(np.mean(pred != true))


def compute_metrics(pred, true):
    """Return ``(bit_accuracy, full_accuracy, hamming_error)``."""
    return bit_accuracy(pred, true), full_accuracy(pred, true), hamming_error(pred, true)


def full_and_bitwise_accuracy(recalled_patterns, true_patterns):
    """Mean full-pattern accuracy and mean bitwise accuracy over a batch."""
    full_acc = np.mean(
        [np.array_equal(r, t) for r, t in zip(recalled_patterns, true_patterns)]
    )
    bit_acc = np.mean(
        [np.mean(r == t) for r, t in zip(recalled_patterns, true_patterns)]
    )
    return full_acc, bit_acc


def pattern_accuracy_pair(pred, true):
    """Return ``(full_match_int, bit_accuracy)`` for a single pattern pair."""
    return int(np.all(pred == true)), float(np.mean(pred == true))


def mean_std_ci(arr, z=1.96):
    """Gaussian mean, standard deviation, and ``z * std / sqrt(n)`` CI half-width."""
    arr = np.asarray(arr, dtype=float)
    mean = np.mean(arr)
    std = np.std(arr)
    ci = z * std / np.sqrt(len(arr))
    return mean, std, ci


def parametric_ci(data, confidence=0.95):
    """Student-t confidence interval around the mean (returns mean, half-width)."""
    a = np.asarray(data, dtype=float)
    n = len(a)
    m = np.mean(a)
    h = sem(a) * t.ppf((1 + confidence) / 2.0, n - 1)
    return m, h


def bootstrap_mean_ci(data, n_boot=2000, confidence=0.95, rng=None):
    """Bootstrap CI for the mean.

    Returns ``(mean, lower, upper)``. Uses a Python loop so the RNG
    consumption order matches the storage-capacity experiment.
    """
    if rng is None:
        rng = np.random
    data = np.asarray(data, dtype=float)
    means = []
    for _ in range(n_boot):
        sample = rng.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))
    lower = np.percentile(means, (1 - confidence) / 2 * 100)
    upper = np.percentile(means, (1 + confidence) / 2 * 100)
    return float(np.mean(data)), float(lower), float(upper)


def bootstrap_percentile_ci(series, n_boot=200, rng=None):
    """Vectorized bootstrap 95% percentile CI. Returns ``(low, high)``."""
    if rng is None:
        rng = np.random
    series = np.asarray(series, dtype=float)
    samples = rng.choice(series, (n_boot, len(series)), replace=True)
    means = samples.mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def cliffs_delta(x, y):
    """Cliff's delta: ``(n_{x>y} - n_{x<y}) / (n_x * n_y)``.

    Positive values mean ``x`` tends to be larger than ``y``.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    greater = 0
    less = 0
    for xi in x:
        greater += np.sum(xi > y)
        less += np.sum(xi < y)
    return (greater - less) / (len(x) * len(y))


def cliffs_delta_magnitude(delta):
    """Standard |δ| interpretation bands."""
    d = abs(delta)
    if d < 0.147:
        return "Negligible"
    if d < 0.33:
        return "Small"
    if d < 0.474:
        return "Medium"
    return "Large"
