# Methodology notes

This document records how the experiments differ. It does not change any of them. Cross-experiment numerical comparisons are only valid when the model, corruption process, and hyperparameters match.

## Models

### Hopfield (classical)

Hebbian storage is shared:

```
W ← (1/m) Σ_μ ξ^μ (ξ^μ)^T ,    diag(W) = 0
```

Recall schedules are **not** shared:

| Experiment | Recall |
|---|---|
| Noise robustness sweep, storage capacity, statistical significance | Synchronous: `x ← sign(Wx)` for 10 steps; zeros mapped to `+1` |
| Scaling | Asynchronous random order: 10 sweeps; `x_i ← +1` if `W_i · x ≥ 0` else `−1` |
| Large-scale inference | Asynchronous sequential index order: 20 sweeps; zeros mapped to `+1`; energy `E = −½ x^T W x` recorded |

### Variational QAM (hybrid)

A PennyLane `default.qubit` circuit is trained with Adam on a mean-squared error between Pauli-Z expectations and the ±1 target pattern. `sign` is applied only at recall, not inside the training loss.

There are four variational architectures in this repository:

| Experiment | Encoding | Ansatz / parameters | Training |
|---|---|---|---|
| Noise robustness sweep | RX(πx) then RY(πx/2) | `Rot` per qubit, linear CNOT; params `(depth, n, 3)`; depth `min(6, n)` | 300 Adam steps, lr=0.05; `__init__` reseeds PennyLane RNG to 42 |
| Storage capacity, circuit depth, convergence | RY(πx) | Per-qubit RY + linear CNOT; params `(depth, n)`; depth `min(8, n)` except depth is swept in the depth study | 100 steps (capacity, depth), 300 steps (convergence); lr=0.05 |
| Scaling | RY(πx) | `Rot` per qubit, linear CNOT; depth `min(6, n)` | 200 steps, minibatch size 2, early stop if loss change `< 1e-4` for 15 steps, lr=0.05 |
| Statistical significance | `PauliX` on qubits where the bit is `−1` | RY + linear CNOT; depth 10 | 100 epochs, lr=0.02; init `N(0, 0.1)` |

These are different models. A result for "QAM" in one CSV is not the same object as "QAM" in another.

### Nearest-neighbor "QAM" proxy

`experiments/noise_robustness_inference.py` does **not** run a quantum circuit. After Hopfield recall, it returns the stored pattern with smallest Hamming distance to the noisy query and labels that row `model="qam"`. That choice made a 128-bit, 300-trial factorial design feasible. It is a classical associative-memory baseline, not the variational QAM.

## Corruption

| Method | Rule | Used by |
|---|---|---|
| Bernoulli | Each bit flips independently with probability `p` | Noise sweep, scaling, statistical significance, inference |
| Fixed count | Flip `max(1, int(n * p))` distinct bits | Storage capacity (`p=0.15`), circuit depth (`p=0.15`) |

Fixed-count corruption still flips **one** bit when `p = 0`, because of `max(1, ...)`. The capacity and depth scripts always use `p = 0.15`, so this branch is unused there, but the helper is written that way.

## Metrics

- **Bit accuracy:** fraction of matching bits.
- **Full-pattern accuracy:** 1 if the recalled vector equals the target, else 0.
- **Hamming error / recovery gain:** used in the inference experiment (`gain = input Hamming error − output Hamming error`).
- **Gaussian 95% CI:** `1.96 * std / sqrt(n)` in the noise sweep and some scaling plots.
- **Bootstrap CI:** 200 resamples (inference, unused helper in scaling), 2000 (capacity), 5000 (statistical significance). Implementations are not identical (loop vs vectorized vs paired-difference bootstrap).
- **Wilcoxon signed-rank tests:** capacity sweep and statistical significance experiment.
- **Cliff's delta:** `scripts/cliffs_delta.py` on the statistical-significance trial rows. Positive δ means Hopfield values tend to exceed QAM values.

## Experiment designs (independent variables)

### Noise robustness sweep

- `n_bits ∈ {4, 6, 8, 10}`
- Bernoulli corruption `∈ {0.0, 0.1, 0.2, 0.3, 0.4}`
- `m = max(1, int(0.3 * n_bits))`
- 30 seeds; multiprocessing over seeds
- Recall tested on every stored pattern

### Large-scale inference

- `n_bits ∈ {8, 12, 16, 24, 32, 48, 64, 96, 128}`
- capacity ratio `∈ {0.1, 0.25, 0.5, 0.75, 1.0}`
- 16 noise levels in `[0, 0.5]`
- 300 trials per cell; one random target pattern per trial
- Hopfield: 20 sequential async steps; QAM column: nearest neighbor

Two critical-noise tables exist on purpose:

- `results/noise_robustness_inference/summary/critical_noise_thresholds.csv` — last noise with mean full accuracy `≥ 0.50` (`scripts/plot_critical_noise_threshold.py`)
- `results/noise_robustness_inference/paper_figures/critical_noise_thresholds.csv` — first noise with mean full accuracy `< 0.90` (`scripts/plot_inference_paper_figures.py`)

### Storage capacity

- `n_bits ∈ {8, 12, 16}`
- `m` from 1 to `n` (for `n=16`, `m ∈ 1..10, 12, 14, 16` to cut runtime)
- 5 trials per `m`; fixed-count 15% noise; bootstrap 2000; Wilcoxon vs QAM

### Scaling

- `n_bits ∈ {4, 6, 8, 12, 16}`
- `m = min(max(1, n_bits // 2), 6)`
- Bernoulli noise `∈ {0.0, 0.1, 0.2, 0.3}`
- 30 trials; seed `123 + trial_id + n_bits * 100`
- QAM is trained once per trial, then evaluated at every noise level

### Circuit depth

- Representative loads `(n, m) ∈ {(8,4), (12,8), (16,12)}`
- `depth ∈ {1, 2, 4, 6, 8, 10, 12}`
- 5 seeds; same RY-linear QAM and 15% fixed-count noise as capacity

### Convergence

- Same `(n, m)` pairs; 300 Adam steps; 3 seeds
- Compares loss at step 100 vs final loss to justify `train_steps=100` in the capacity sweep

### Statistical significance

- `n_bits ∈ {8, 12, 16}`, capacity `∈ {0.2, 0.3, 0.4, 0.5}`, noise `∈ {0.1, 0.2}`
- 30 seeds; paired bootstrap on QAM − Hopfield; Wilcoxon tests

## Issues noted but not changed

These are scientific or software quirks left intact so published numbers stay aligned with the original scripts:

1. The inference experiment's `qam` label is a nearest-neighbor proxy.
2. QAM architectures and Hopfield update rules differ across experiments.
3. The noise-sweep `QAM.__init__` reseeds PennyLane numpy to 42 after the trial seed was set, so QAM parameters are less trial-randomized than the Hopfield weights.
4. Scaling uses PennyLane numpy for pattern generation **and** for Hopfield update permutations (same RNG stream).
5. Capacity/depth `corrupt_fixed_count` uses `max(1, int(n * p))`.
6. Wilcoxon calls used a bare `except:` originally; the reorganized scripts catch `Exception` and still return `None` / `1.0` as before.
7. Several original scripts wrote to `results/` or `results_scaling/` while the saved files actually lived in `*_results/` folders (manual moves). Output paths are now consistent.
8. `tqdm` was imported by the capacity sweep but missing from the old `requirements.txt`.
9. Timing conventions differ (per bit vs per pattern vs wall-clock for the whole recall loop).
