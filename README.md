# Hybrid Quantum-Classical Associative Memory

Classical Hopfield networks and hybrid variational quantum associative memory (QAM) models, compared on bipolar pattern recall under noise, storage load, system size, and circuit depth.

This is a small research codebase for reproducing those comparisons. It does **not** claim a practical quantum advantage. Several experiments use different QAM circuits, and one large-scale study uses a classical nearest-neighbor proxy labeled `qam` in its CSVs. See `docs/methodology.md` before interpreting results across experiments.

## Research question

How does a hybrid variational quantum associative memory compare with a classical Hopfield network on:

1. **Noise robustness** — recall from bit-flip-corrupted queries
2. **Storage capacity** — accuracy as the number of stored patterns grows
3. **Scaling** — accuracy, runtime, and parameter count vs pattern length
4. **Circuit depth** — whether QAM recall is limited by ansatz depth
5. **Statistical comparison** — bootstrap confidence intervals and Wilcoxon tests on accuracy gaps

The Hopfield baseline is a discrete bipolar network with Hebbian weights. The QAM models are hybrid: a parameterized quantum circuit is trained classically (Adam on a mean-squared readout loss) on a CPU simulator (`default.qubit`).

## Repository structure

```
src/                  Shared models and utilities (import as ``src.*``)
experiments/          Independently runnable experiment modules
scripts/              Plotting, effect-size, and convenience runners
results/<experiment>/ Preserved outputs (raw / summary / plots)
tests/                Import and path checks (not scientific experiments)
docs/                 Methodology notes
pyproject.toml        Editable install and dependencies
```

Each experiment writes under `results/<experiment_name>/` using project-root paths, so the current working directory does not matter.

## Importing models

Shared code is imported from `src`:

```python
from src.hopfield import Hopfield
from src.qam import train_ry_linear_qam, qam_recall
from src.paths import PROJECT_ROOT, results_subdir
```

`src.qam` does **not** export a class named `QAM` or `QuantumAssociativeMemory`. The RY-linear variational circuit is a set of functions. Other experiments keep their own local `QAM` class or a nearest-neighbor proxy because those circuits are different models. See `docs/methodology.md`.

## Installation

Python 3.10+ recommended. From the project root:

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -e .
```

That editable install makes `src`, `experiments`, and `scripts` importable without `sys.path` hacks. For the import/path checks:

```bash
pip install -e ".[dev]"
pytest
```

Pinned scientific dependencies are listed in `requirements.txt` and mirrored in `pyproject.toml`.

## How to run individual experiments

Canonical form (from the project root, after `pip install -e .`):

```bash
python -m experiments.noise_robustness_sweep
python -m experiments.noise_robustness_inference
python -m experiments.storage_capacity
python -m experiments.scaling
python -m experiments.circuit_depth
python -m experiments.convergence
python -m experiments.statistical_significance
```

Direct file execution (`python experiments/storage_capacity.py`) also works after the editable install, because `src` is on the Python path. Prefer `python -m` so multiprocessing workers import the experiment as a real module.

List experiments without running them:

```bash
python -m scripts.run_all_experiments
```

Run one by name (still expensive):

```bash
python -m scripts.run_all_experiments --only convergence
```

`noise_robustness_inference.py` and `statistical_significance.py` are the longest jobs. Re-running an experiment overwrites CSVs in that experiment's results directory; existing files are not deleted first.

## How results are organized

Existing outputs were moved, not regenerated. Original filenames are kept.

| Experiment | Results directory | Typical contents |
|---|---|---|
| Noise robustness sweep | `results/noise_robustness_sweep/` | aggregated CSV, accuracy-vs-noise plots |
| Large-scale inference | `results/noise_robustness_inference/` | per-trial CSV (`raw/`), summary CSV, paper figures |
| Storage capacity | `results/storage_capacity/` | sweep CSV, phase-transition CSV, plots |
| Scaling | `results/scaling/` | per-trial CSV (`raw/`), seaborn plots |
| Circuit depth | `results/circuit_depth/` | depth-sweep CSV, plots |
| Convergence | `results/convergence/` | per-config loss CSVs, summary, plots |
| Statistical significance | `results/statistical_significance/` | trial rows, summary, Cliff's delta, CI plots |

Where it was unambiguous, files sit in `raw/`, `summary/`, or `plots/`. The inference experiment also keeps `paper_figures/` (those plots used a different critical-threshold definition than `summary/critical_noise_thresholds.csv`).

Plotting scripts (do not need to re-run experiments):

```bash
python -m scripts.plot_noise_robustness_sweep
python -m scripts.plot_noise_robustness_inference
python -m scripts.plot_scaling
python -m scripts.plot_inference_paper_figures
python -m scripts.plot_critical_noise_threshold
python -m scripts.cliffs_delta
python -m scripts.plot_bootstrap_distribution
```

## Main dependencies

- `numpy`, `pandas`, `scipy` — numerics and summaries
- `pennylane` — variational circuits on `default.qubit`
- `matplotlib`, `seaborn` — figures
- `tqdm` — progress bar in the capacity sweep
- `psutil` — optional system-info printout in the noise sweep

## Reproducibility notes

- Scripts seed NumPy (and PennyLane numpy where used) per trial.
- Result paths are built from `src/paths.py` (`pathlib`), not from the process cwd.
- Install with `pip install -e .` so `from src...` works without modifying `sys.path`.
- `if __name__ == "__main__"` guards keep experiment bodies from running on import.
- Full experiments were not re-run as part of this repository cleanup. The CSVs and figures under `results/` are the original saved outputs.
- **Do not pool QAM numbers across experiments.** Circuit, encoding, training budget, Hopfield update rule, and even the definition of "QAM" differ. Details are in `docs/methodology.md`.

## Classical Hopfield vs hybrid QAM

**Hopfield.** Patterns are stored with a Hebbian outer-product rule (`W` has a zero diagonal). Recall is a discrete ±1 dynamics. Most experiments use synchronous `sign(Wx)` updates; the scaling experiment uses random-order asynchronous updates; the large-scale inference experiment uses sequential asynchronous updates and also records Hopfield energy.

**Variational QAM.** A quantum circuit encodes a query, applies a shallow parameterized ansatz, and measures Pauli-Z expectations. Training is classical (Adam) on a mean-squared error between the measured vector and the stored pattern. Recall applies `sign` to the measured vector. This is a hybrid quantum-classical model simulated on a CPU, not a demonstration of quantum computational advantage.

**Inference experiment exception.** In `experiments/noise_robustness_inference.py`, the column labeled `qam` is a nearest-neighbor match in Hamming distance. That study scales to 128 bits, where variational simulation was not used. Treat those `qam` rows as a classical proxy, not as the variational QAM from the other scripts.
