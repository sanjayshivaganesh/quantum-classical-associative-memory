"""Cliff's delta effect sizes from the statistical-significance trial rows."""

import pandas as pd

from src.metrics import cliffs_delta, cliffs_delta_magnitude
from src.paths import results_subdir


def main():
    raw_dir = results_subdir("statistical_significance", "raw")
    summary_dir = results_subdir("statistical_significance", "summary")
    csv_path = raw_dir / "statistical_rows.csv"

    df = pd.read_csv(csv_path)

    required_columns = [
        "n_bits",
        "capacity_ratio",
        "noise",
        "hopfield_full",
        "hopfield_bit",
        "qam_full",
        "qam_bit",
    ]

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns:\n{missing}"
        )

    rows = []
    group_cols = ["n_bits", "capacity_ratio", "noise"]

    for (n_bits, cap_ratio, noise), group in df.groupby(group_cols):

        delta_full = cliffs_delta(
            group["hopfield_full"].values,
            group["qam_full"].values
        )

        delta_bit = cliffs_delta(
            group["hopfield_bit"].values,
            group["qam_bit"].values
        )

        rows.append({
            "n_bits": n_bits,
            "capacity_ratio": cap_ratio,
            "noise": noise,
            "delta_full": round(delta_full, 3),
            "full_magnitude": cliffs_delta_magnitude(delta_full),
            "delta_bit": round(delta_bit, 3),
            "bit_magnitude": cliffs_delta_magnitude(delta_bit)
        })

    results = pd.DataFrame(rows)
    results = results.sort_values(
        ["n_bits", "capacity_ratio", "noise"]
    )

    out_path = summary_dir / "cliffs_delta_table.csv"
    results.to_csv(out_path, index=False)

    print("\n")
    print("=" * 72)
    print("CLIFF'S DELTA EFFECT SIZES")
    print("=" * 72)

    print(results.to_string(index=False))

    print("=" * 72)

    print("\nInterpretation")
    print("----------------------------")
    print("|δ| < 0.147  : Negligible")
    print("|δ| < 0.330  : Small")
    print("|δ| < 0.474  : Medium")
    print("|δ| ≥ 0.474  : Large")
    print("Positive δ means Hopfield scores tend to exceed QAM scores.")

    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
