"""Shared model and utility code for the associative-memory experiments.

Import the concrete modules, for example::

    from src.hopfield import Hopfield
    from src.qam import train_ry_linear_qam, qam_recall
    from src.paths import PROJECT_ROOT, results_subdir

``src.qam`` does not define a class named ``QAM``. Several experiments keep
their own QAM circuit or a classical nearest-neighbor proxy because those
models are not interchangeable. See ``docs/methodology.md``.
"""
