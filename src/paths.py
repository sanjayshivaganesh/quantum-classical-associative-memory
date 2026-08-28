"""Project-root and results-directory helpers.

All experiment and plotting scripts should resolve output locations through
these helpers so they work regardless of the current working directory.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def experiment_dir(name: str) -> Path:
    """Return ``results/<name>/``, creating it if needed."""
    path = PROJECT_ROOT / "results" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def results_subdir(experiment_name: str, *parts: str) -> Path:
    """Return a subdirectory under ``results/<experiment_name>/``.

    Example: ``results_subdir("scaling", "plots")``
    -> ``<project>/results/scaling/plots/``
    """
    path = experiment_dir(experiment_name).joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path
