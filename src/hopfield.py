"""Classical Hopfield associative memory with Hebbian storage.

This repository uses more than one recall schedule. They are not
interchangeable:

- ``Hopfield`` — synchronous ``sign(W x)`` updates (noise sweep, storage
  capacity, statistical significance).
- ``hopfield_async_sequential_recall`` — fixed-index sequential updates
  with energy tracking (large-scale inference experiment).
- ``HopfieldAsyncRandom`` — random-order sequential updates using the
  PennyLane numpy RNG (scaling experiment). That class lives here so the
  scaling script does not re-implement Hebbian storage, but it must keep
  using PennyLane's RNG stream to preserve the original trial behavior.
"""

import time
import numpy as np


class Hopfield:
    """Synchronous discrete Hopfield network."""

    def __init__(self, n_bits, steps=10):
        self.n_bits = n_bits
        self.steps = steps
        self.W = np.zeros((n_bits, n_bits))

    def train(self, patterns):
        start_time = time.time()
        self.W = np.zeros((self.n_bits, self.n_bits))
        for p in patterns:
            self.W += np.outer(p, p)
        np.fill_diagonal(self.W, 0)
        self.W /= len(patterns)
        return time.time() - start_time

    def recall(self, pattern, steps=None):
        n_steps = self.steps if steps is None else steps
        x = np.asarray(pattern).copy()
        for _ in range(n_steps):
            x = np.sign(self.W @ x)
            x[x == 0] = 1
        return x

    def recall_timed(self, pattern, steps=None):
        """Return ``(recalled_pattern, inference_time / n_bits)``.

        Matches the timing convention in the original noise-robustness sweep.
        """
        start_time = time.time()
        x = self.recall(pattern, steps=steps)
        return x, (time.time() - start_time) / len(pattern)


def hopfield_hebbian_weights(patterns):
    """Hebbian weight matrix with zero diagonal, normalized by pattern count."""
    n_patterns = len(patterns)
    W = (np.asarray(patterns).T @ np.asarray(patterns)) / n_patterns
    np.fill_diagonal(W, 0)
    return W


def hopfield_async_sequential_recall(W, noisy_input, steps=20):
    """Asynchronous sequential recall used by the inference experiment.

    Returns ``(final_state, final_energy, energy_drop)``.
    """
    state = noisy_input.copy()
    input_energy = -0.5 * noisy_input @ W @ noisy_input
    n_bits = len(state)
    for _ in range(steps):
        for i in range(n_bits):
            s = np.sign(np.dot(W[i], state))
            state[i] = 1 if s == 0 else s
    final_energy = -0.5 * state @ W @ state
    energy_drop = input_energy - final_energy
    return state, final_energy, energy_drop


class HopfieldAsyncRandom:
    """Hopfield network with random-order asynchronous updates.

    Uses PennyLane's numpy RNG for the update permutation so the scaling
    experiment consumes the same random stream as the original script
    (which imported ``pennylane.numpy as np`` for both patterns and recall).
    """

    def __init__(self, n_bits, steps=10):
        from pennylane import numpy as pnp

        self.n_bits = n_bits
        self.steps = steps
        self.W = pnp.zeros((n_bits, n_bits))

    def train(self, patterns):
        from pennylane import numpy as pnp

        self.W = pnp.zeros((self.n_bits, self.n_bits))
        for p in patterns:
            self.W += pnp.outer(p, p)
        pnp.fill_diagonal(self.W, 0)
        self.W /= len(patterns)

    def recall(self, x, steps=None):
        from pennylane import numpy as pnp

        n_steps = self.steps if steps is None else steps
        v = x.copy()
        for _ in range(n_steps):
            for i in pnp.random.permutation(self.n_bits):
                s = np.dot(self.W[i], v)
                v[i] = 1 if s >= 0 else -1
        return v
