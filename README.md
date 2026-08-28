# Hybrid Quantum-Classical Associative Memory

Classical Hopfield networks and hybrid variational quantum associative memory (QAM) models, compared on bipolar pattern recall under noise, storage load, system size, and circuit depth.

This repository contains the code and saved results for the experiments in my research paper. The goal is to compare a classical Hopfield network with a hybrid quantum-classical associative memory model across several different conditions.

This work does **not** claim a practical quantum advantage. The QAM implementations also differ between experiments, so the results should not be treated as measurements of one single QAM model. In particular, one of the larger experiments uses a classical nearest-neighbor proxy labeled `qam` rather than the variational quantum circuit. See [`docs/methodology.md`](docs/methodology.md) before comparing results between experiments.

## Research question

How does a hybrid variational quantum associative memory compare with a classical Hopfield network on:

- **Noise robustness** — recall from bit-flip-corrupted queries
- **Storage capacity** — accuracy as the number of stored patterns increases
- **Scaling** — accuracy, runtime, and parameter count as pattern length increases
- **Circuit depth** — whether QAM recall changes with ansatz depth
- **Statistical comparison** — bootstrap confidence intervals and Wilcoxon tests on accuracy gaps

The Hopfield baseline is a discrete bipolar network using Hebbian weights.

The main QAM model is a hybrid model: a parameterized quantum circuit is trained classically using Adam and a mean-squared readout loss. The quantum circuits are simulated on a CPU using PennyLane's `default.qubit`.

## Repository structure

```text
src/                  Shared models and utilities
experiments/          Individual experiment modules
scripts/              Plotting and analysis scripts
results/              Saved experimental outputs
tests/                Import and path checks
docs/                 Methodology notes
pyproject.toml        Project configuration and dependencies
requirements.txt      Pinned dependencies
```

Each experiment writes to its own directory under `results/`. Paths are built from the project root, so the experiments do not depend on the directory from which they are run.

## Models

### Hopfield network

The Hopfield implementation stores bipolar patterns using the Hebbian outer-product rule, with a zero diagonal in the weight matrix.

Recall uses discrete `±1` updates. Most experiments use synchronous updates, while some of the scaling and inference experiments use asynchronous updates.

The exact update rule for each experiment is documented in [`docs/methodology.md`](docs/methodology.md).

### Variational QAM

The main QAM implementation uses a parameterized quantum circuit to transform a noisy query and reconstruct a stored bipolar pattern.

Training is classical:

1. Encode the query into the circuit.
2. Apply the parameterized ansatz.
3. Measure Pauli-Z expectation values.
4. Compare the output with the target pattern using mean-squared error.
5. Update the circuit parameters using Adam.

During recall, the measured values are converted back to bipolar values using their signs.

This is a **hybrid quantum-classical model running on a classical simulator**. The experiments therefore do not demonstrate a quantum speedup.

## Important: the QAM models are not all the same

The different experiments were developed around different circuit designs and experimental requirements. They can therefore have different:

- circuit architectures
- training budgets
- encodings
- retrieval procedures
- system sizes
- Hopfield update rules
- definitions of the QAM baseline

For this reason, **QAM results should not be pooled across experiments without checking the methodology first.**

There is one particularly important exception.

### `noise_robustness_inference`

The `qam` column in `experiments/noise_robustness_inference.py` is a **classical nearest-neighbor baseline using Hamming distance**.

This experiment goes up to 128-bit patterns, where the variational quantum simulation used in the other experiments was not used.

So these `qam` results are a **classical proxy**, not results from the variational QAM circuit.

The exact differences between experiments are documented in [`docs/methodology.md`](docs/methodology.md).

## Installation

Python 3.10+ is recommended.

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

For the test dependencies:

```bash
pip install -e ".[dev]"
pytest
```

The editable install makes `src`, `experiments`, and `scripts` importable without `sys.path` modifications.

## Running the experiments

Experiments can be run individually with:

```bash
python -m experiments.noise_robustness_sweep
python -m experiments.noise_robustness_inference
python -m experiments.storage_capacity
python -m experiments.scaling
python -m experiments.circuit_depth
python -m experiments.convergence
python -m experiments.statistical_significance
```

There is also a convenience runner:

```bash
python -m scripts.run_all_experiments
```

or, for a single experiment:

```bash
python -m scripts.run_all_experiments --only convergence
```

Some experiments are considerably slower than others. In particular, `noise_robustness_inference.py` and `statistical_significance.py` can take a long time to finish.

I recommend using `python -m` rather than running the files directly, especially for experiments that use multiprocessing.

Re-running an experiment overwrites the CSV files in that experiment's results directory. Existing files are not deleted first.

## Results

The existing results were moved into the repository rather than regenerated during the repository cleanup.

```text
results/
├── noise_robustness_sweep/
├── noise_robustness_inference/
├── storage_capacity/
├── scaling/
├── circuit_depth/
├── convergence/
└── statistical_significance/
```

Typical outputs include raw trial data, summary CSVs, and plots.

The inference experiment also contains `paper_figures/`. These figures use a different critical-noise threshold definition from `summary/critical_noise_thresholds.csv`, so those two analyses should not be treated as identical.

## Plotting saved results

The plotting scripts do not require the experiments to be run again if the required result files are already present.

```bash
python -m scripts.plot_noise_robustness_sweep
python -m scripts.plot_noise_robustness_inference
python -m scripts.plot_scaling
python -m scripts.plot_inference_paper_figures
python -m scripts.plot_critical_noise_threshold
python -m scripts.cliffs_delta
python -m scripts.plot_bootstrap_distribution
```

## Statistical analysis

The statistical experiments include:

- bootstrap confidence intervals
- Wilcoxon signed-rank tests
- accuracy-gap analysis
- Cliff's delta effect sizes

These are used to measure how consistently the two approaches differ under the tested conditions.

A statistically significant difference should not be interpreted as evidence of quantum advantage. It only shows that a difference was observed between the specific models and experimental conditions being compared.

## Reproducibility

The experiment scripts seed NumPy, and PennyLane's NumPy interface where applicable, on a per-trial basis.

Result paths are handled through `src/paths.py` using `pathlib`.

Experiment code is protected by `if __name__ == "__main__":` guards so importing a module does not start an experiment.

The CSVs and figures currently in `results/` are the original saved outputs. The full experiments were **not re-run as part of the repository cleanup**.

## Imports

The shared models are imported from `src`:

```python
from src.hopfield import Hopfield
from src.qam import train_ry_linear_qam, qam_recall
from src.paths import PROJECT_ROOT, results_subdir
```

`src.qam` does not contain a `QAM` or `QuantumAssociativeMemory` class. The RY-linear QAM implementation is function-based.

Some other experiments have their own local QAM class because they use different circuits.

## Dependencies

The main dependencies are:

- NumPy
- pandas
- SciPy
- PennyLane
- matplotlib
- seaborn
- tqdm
- psutil

The complete dependency lists are in `pyproject.toml` and `requirements.txt`.

## Limitations

The results in this repository apply to the particular models and experimental settings used here.

In particular, this work does not establish that:

- quantum associative memory is generally worse than classical associative memory;
- variational quantum circuits cannot outperform Hopfield networks;
- the implemented QAM architecture represents all possible quantum associative-memory approaches;
- CPU simulation represents the performance of actual quantum hardware;
- increasing circuit depth should always improve recall.

The main comparison is between a **classical Hopfield attractor-based memory** and a **specific hybrid variational reconstruction model**. Differences between the two therefore cannot automatically be attributed to "classical vs. quantum" computation.

## Research paper

The corresponding research paper is:

**Comparing Classical Hopfield Networks and Hybrid Quantum-Classical Models for Associative Memory**

The paper contains the full research discussion and interpretation of the experiments. This repository contains the implementation, saved results, and analysis scripts used for the study.