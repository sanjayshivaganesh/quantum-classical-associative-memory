# Reorganization Plan

Audit of the research codebase before any file moves or refactors.
Ignored: `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.git/`.

## Current relevant structure

All experiment scripts and most plotting scripts live in the project root. Result folders use inconsistent names (`results_*`, `*_results`). Several scripts write to a generic `results/` directory that does not match where the saved outputs actually live.

```
ResearchCode/
├── requirements.txt
├── noise_robustness_sweep.py          # variational QAM vs Hopfield, small n
├── noise_robustness_inference.py      # large-n inference; QAM is nearest-neighbor proxy
├── storage_capacity_sweep.py
├── scale_sweep.py
├── depth_scaling.py
├── convergence_check.py
├── statist_sig_ci.py
├── plot_noise_robustness_sweep.py
├── plot_inference_results.py
├── plot_scaling_results.py
├── noise_robustness_sweep_results/
├── noise_robustness_inference_results/  # includes generate_plots.py, ct_vs_cr.py, paper_figures/
├── results_storage_capacity/
├── scale_sweep_results/                 # CSV + plots/ (script writes to results_scaling, which does not exist)
├── results_depth_scaling/
├── convergence_results/
├── statist_sig_ci_results/              # includes cliffsdelta.py, bootstrap_distributionfig.py
├── experiment.log                       # noise_robustness_inference run log
├── noise_robustness_sweep_results/experiment.log
├── storage_capacity_sweep.log
├── depth_scaling.log
└── convergence.log
```

No existing README, `.gitignore`, `src/`, `experiments/`, `scripts/`, or `docs/`.

## Experiments found

| Script | Independent variables | Model notes | Output (actual) |
|---|---|---|---|
| `noise_robustness_sweep.py` | n_bits ∈ {4,6,8,10}, corruption ∈ {0,0.1,0.2,0.3,0.4}, 30 trials, capacity_ratio=0.3 | Sync Hopfield; Rot-ansatz variational QAM (RX+RY encode, `Rot`, depth=6, 300 steps) | `noise_robustness_sweep_results/` (script writes `results/`) |
| `noise_robustness_inference.py` | n ∈ {8…128}, capacity ratios, 16 noise levels, 300 trials | Async sequential Hopfield (20 steps); **QAM = nearest-neighbor Hamming proxy, not a quantum circuit** | `noise_robustness_inference_results/` |
| `storage_capacity_sweep.py` | n ∈ {8,12,16}, m sweep, 5 trials, recall_noise=0.15 | Sync Hopfield; RY-linear variational QAM (depth=min(8,n), 100 steps) | `results_storage_capacity/` |
| `scale_sweep.py` | n ∈ {4,6,8,12,16}, noise ∈ {0,0.1,0.2,0.3}, 30 trials | Async random-order Hopfield; Rot-ansatz QAM with minibatch + early stopping | `scale_sweep_results/` (script writes `results_scaling/`) |
| `depth_scaling.py` | n ∈ {8,12,16} with fixed m, depth ∈ {1…12}, 5 trials | QAM only (same RY-linear ansatz as capacity) | `results_depth_scaling/` |
| `convergence_check.py` | (n,m) ∈ {(8,4),(12,8),(16,12)}, 300 train steps, 3 seeds | QAM only (same RY-linear ansatz; records loss) | `convergence_results/` |
| `statist_sig_ci.py` | n ∈ {8,12,16}, cap ∈ {0.2…0.5}, noise ∈ {0.1,0.2}, 30 seeds | Sync Hopfield; PauliX-encoding RY QAM (depth=10, 100 epochs, lr=0.02) | `statist_sig_ci_results/` (script writes `results/`) |

Post-processing scripts (not full experiments):

- `plot_noise_robustness_sweep.py`, `plot_inference_results.py`, `plot_scaling_results.py`
- `noise_robustness_inference_results/generate_plots.py`, `ct_vs_cr.py`
- `statist_sig_ci_results/cliffsdelta.py`, `bootstrap_distributionfig.py`

## Duplicated code found

**Hopfield (Hebbian train is shared; recall is not):**

- Synchronous `sign(Wx)` , 10 steps: noise sweep, storage capacity, statistical significance
- Asynchronous random permutation, `v[i]=1 if s>=0 else -1`: scaling
- Asynchronous sequential index order, 20 steps, energy tracking: inference

**Variational QAM (four incompatible circuits — must not be merged):**

1. Rot ansatz, RX+RY encoding, params `(depth, n, 3)` — noise robustness sweep
2. RY-linear ansatz, RY encoding, params `(depth, n)` — storage capacity, depth scaling, convergence
3. Rot ansatz, RY encoding, minibatch + early stopping — scaling
4. PauliX encoding of −1 bits, RY layers, depth=10, lr=0.02 — statistical significance

**QAM proxy (not variational):** nearest-neighbor Hamming match — inference experiment only.

**Corruption:**

- Bernoulli bit-flip (`rand < p`): noise sweep, scaling, stats, inference
- Fixed-count bit-flip (`n_flip = max(1, int(n * p))`): storage capacity, depth scaling

**Metrics / CI:** full-pattern vs bitwise accuracy duplicated everywhere; Gaussian 95% CI (`1.96 * std / sqrt(n)`); bootstrap CI with n_boot ∈ {200, 2000, 5000}; Wilcoxon tests in capacity and stats experiments.

**Timing:** `time.time()` wrappers around train/recall, with slightly different normalizations (per bit vs per pattern).

**Plotting:** matplotlib errorbar/line plots duplicated per experiment; seaborn used only in scaling plots.

## File classification

| Category | Files |
|---|---|
| Reusable model/source | None yet (all inlined in experiment scripts) |
| Experiment runners | `noise_robustness_sweep.py`, `noise_robustness_inference.py`, `storage_capacity_sweep.py`, `scale_sweep.py`, `depth_scaling.py`, `convergence_check.py`, `statist_sig_ci.py` |
| Plotting scripts | `plot_*.py`, `generate_plots.py`, `ct_vs_cr.py`, `bootstrap_distributionfig.py` |
| Utility scripts | `cliffsdelta.py` |
| Raw results | `noise_inference_rows.csv` (~50 MB), `scaling_sweep.csv`, `statistical_rows.csv`, `convergence_n*_m*.csv` |
| Summary results | aggregated CSVs, `phase_transition.csv`, `experiment_summary.txt`, `cliffs_delta_table.csv`, `critical_noise_thresholds.csv` (two versions with different threshold definitions) |
| Generated figures | all `.png` files in result folders |
| Run logs | `*.log` |
| Not source | `venv/` |

## Proposed target structure

```
project-root/
├── README.md
├── REORGANIZATION_PLAN.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── paths.py
│   ├── hopfield.py          # synchronous Hebbian Hopfield + documented async helpers
│   ├── qam.py               # RY-linear QAM (shared by capacity/depth/convergence)
│   ├── data_generation.py   # random bipolar patterns + both corruption methods
│   └── metrics.py           # accuracy, Gaussian CI, bootstrap CI
├── experiments/
│   ├── noise_robustness_sweep.py
│   ├── noise_robustness_inference.py
│   ├── storage_capacity.py
│   ├── scaling.py
│   ├── circuit_depth.py
│   ├── convergence.py
│   └── statistical_significance.py
├── scripts/
│   ├── run_all_experiments.py
│   ├── plot_noise_robustness_sweep.py
│   ├── plot_noise_robustness_inference.py
│   ├── plot_scaling.py
│   ├── plot_inference_paper_figures.py
│   ├── plot_critical_noise_threshold.py
│   ├── cliffs_delta.py
│   └── plot_bootstrap_distribution.py
├── results/
│   ├── noise_robustness_sweep/{summary,plots}/
│   ├── noise_robustness_inference/{raw,summary,plots,paper_figures}/
│   ├── storage_capacity/{summary,plots}/
│   ├── scaling/{raw,plots}/
│   ├── circuit_depth/{summary,plots}/
│   ├── convergence/{raw,summary,plots}/
│   └── statistical_significance/{raw,summary,plots}/
└── docs/
    └── methodology.md
```

Two distinct noise studies keep distinct names. `raw/` / `summary/` / `plots/` are used only where the existing files fit; original filenames are preserved.

## Planned file moves

**Experiments (root → `experiments/`, renamed for clarity):**

- `noise_robustness_sweep.py` → `experiments/noise_robustness_sweep.py`
- `noise_robustness_inference.py` → `experiments/noise_robustness_inference.py`
- `storage_capacity_sweep.py` → `experiments/storage_capacity.py`
- `scale_sweep.py` → `experiments/scaling.py`
- `depth_scaling.py` → `experiments/circuit_depth.py`
- `convergence_check.py` → `experiments/convergence.py`
- `statist_sig_ci.py` → `experiments/statistical_significance.py`

**Plotting / utilities (→ `scripts/`):**

- `plot_noise_robustness_sweep.py`, `plot_inference_results.py`, `plot_scaling_results.py`
- `noise_robustness_inference_results/generate_plots.py` → `scripts/plot_inference_paper_figures.py`
- `noise_robustness_inference_results/ct_vs_cr.py` → `scripts/plot_critical_noise_threshold.py`
- `statist_sig_ci_results/cliffsdelta.py` → `scripts/cliffs_delta.py`
- `statist_sig_ci_results/bootstrap_distributionfig.py` → `scripts/plot_bootstrap_distribution.py`

**Results (preserve every CSV/PNG/TXT; keep original filenames):**

- `noise_robustness_sweep_results/*.csv` → `results/noise_robustness_sweep/summary/`
- `noise_robustness_sweep_results/*.png` → `results/noise_robustness_sweep/plots/`
- `noise_robustness_inference_results/noise_inference_rows.csv` → `results/noise_robustness_inference/raw/`
- `noise_robustness_inference_results/*summary*.csv`, `critical_noise_thresholds.csv` → `.../summary/`
- `noise_robustness_inference_results/*.png` → `.../plots/`
- `noise_robustness_inference_results/paper_figures/` → `results/noise_robustness_inference/paper_figures/` (unchanged internally)
- `results_storage_capacity/*.csv`, `experiment_summary.txt` → `results/storage_capacity/summary/`
- `results_storage_capacity/*.png` → `results/storage_capacity/plots/`
- `scale_sweep_results/scaling_sweep.csv` → `results/scaling/raw/`
- `scale_sweep_results/plots/` → `results/scaling/plots/`
- `results_depth_scaling/depth_scaling.csv` → `results/circuit_depth/summary/`
- `results_depth_scaling/*.png` → `results/circuit_depth/plots/`
- `convergence_results/convergence_n*.csv` → `results/convergence/raw/`
- `convergence_results/convergence_summary.csv` → `results/convergence/summary/`
- `convergence_results/*.png` → `results/convergence/plots/`
- `statist_sig_ci_results/statistical_rows.csv` → `results/statistical_significance/raw/`
- `statist_sig_ci_results/statistical_summary.csv`, `cliffs_delta_table.csv` → `.../summary/`
- `statist_sig_ci_results/*.png` → `.../plots/`
- Run logs → corresponding `results/<experiment>/` directories

## Planned shared modules

- `src/paths.py` — `PROJECT_ROOT` via `pathlib`; experiment result directories
- `src/hopfield.py` — synchronous Hebbian `Hopfield` (the duplicated class). Inference sequential recall and energy helpers live here too. Scaling keeps a local async-random class **or** imports a dedicated helper that still uses the PennyLane numpy RNG stream (required for numerical equivalence)
- `src/qam.py` — RY-linear variational QAM used by capacity, depth, and convergence. Other QAM architectures stay in their experiment files (they are scientifically different models, not copies)
- `src/data_generation.py` — `random_bipolar_patterns`, Bernoulli corruption, fixed-count corruption
- `src/metrics.py` — full/bitwise accuracy, Gaussian CI, bootstrap mean CI

Not extracted into a single QAM class: Rot-ansatz, minibatch Rot-ansatz, PauliX-encoding QAM, nearest-neighbor proxy.

## Expected import/path changes

Every experiment/script will prepend the project root to `sys.path` and import `src.*`.

Output paths switch from cwd-relative strings to `src.paths` directories:

| Script | Old path | New path |
|---|---|---|
| noise_robustness_sweep | `results/noise_robustness_sweep.csv` | `results/noise_robustness_sweep/summary/` |
| noise_robustness_inference | `noise_robustness_inference_results/` | `results/noise_robustness_inference/` |
| storage_capacity | `results_storage_capacity/` | `results/storage_capacity/` |
| scaling | `results_scaling/` (broken vs actual `scale_sweep_results/`) | `results/scaling/` |
| circuit_depth | `results_depth_scaling/` | `results/circuit_depth/` |
| convergence | `convergence_results/` | `results/convergence/` |
| statistical_significance | `results/` (actual files in `statist_sig_ci_results/`) | `results/statistical_significance/` |
| plot_scaling_results | `results_scaling/` | `results/scaling/` |
| generate_plots / ct_vs_cr | CWD-relative CSVs inside the results folder | pathlib to `results/noise_robustness_inference/` |
| cliffsdelta / bootstrap fig | CWD-relative inside `statist_sig_ci_results/` | pathlib to `results/statistical_significance/` |

`if __name__ == "__main__"` guards will be added around experiment bodies that currently execute at import time (`storage_capacity_sweep.py`, `scale_sweep.py`, `depth_scaling.py`, `convergence_check.py`). This is a software fix, not a methodology change.

## Constraints to preserve

- Do not unify QAM architectures.
- Do not change hyperparameters, trial counts, seeds, or update rules.
- Do not delete or rewrite existing CSV/PNG results.
- Do not regenerate plots as part of this reorganization.
- Do not run full experiments during validation.
- Document, but do not “fix,” scientific inconsistencies (especially the inference experiment’s nearest-neighbor QAM proxy).
