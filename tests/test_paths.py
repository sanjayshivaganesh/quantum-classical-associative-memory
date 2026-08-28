"""Verify result paths resolve from the repository, not the process cwd."""

from src.paths import PROJECT_ROOT, experiment_dir, results_subdir


def test_project_root_is_repository_root():
    assert PROJECT_ROOT.is_absolute()
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "src" / "paths.py").is_file()
    assert (PROJECT_ROOT / "experiments").is_dir()


def test_results_subdir_is_under_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = results_subdir("path_audit_probe_subdir", "summary")
    assert path.is_dir()
    assert path == PROJECT_ROOT / "results" / "path_audit_probe_subdir" / "summary"
    assert path.is_absolute()
    probe = PROJECT_ROOT / "results" / "path_audit_probe_subdir"
    summary = probe / "summary"
    if summary.exists():
        summary.rmdir()
    if probe.exists() and not any(probe.iterdir()):
        probe.rmdir()


def test_experiment_dir_does_not_use_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = experiment_dir("path_audit_probe_dir")
    assert path.parent == PROJECT_ROOT / "results"
    if path.exists() and not any(path.iterdir()):
        path.rmdir()


def test_existing_result_csv_is_findable():
    csv_path = (
        PROJECT_ROOT
        / "results"
        / "noise_robustness_sweep"
        / "summary"
        / "noise_robustness_sweep.csv"
    )
    assert csv_path.is_file()
