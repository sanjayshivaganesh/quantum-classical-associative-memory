"""Bootstrap distributions of mean full-recall accuracy (stats experiment)."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.paths import results_subdir


BOOTSTRAPS = 5000


def main():
    raw_dir = results_subdir("statistical_significance", "raw")
    plots_dir = results_subdir("statistical_significance", "plots")
    csv_path = raw_dir / "statistical_rows.csv"

    df = pd.read_csv(csv_path)

    hf = df["hopfield_full"].values
    qam = df["qam_full"].values

    hf_boot = []
    qam_boot = []

    for _ in range(BOOTSTRAPS):

        idx_h = np.random.randint(0, len(hf), len(hf))
        idx_q = np.random.randint(0, len(qam), len(qam))

        hf_boot.append(np.mean(hf[idx_h]))
        qam_boot.append(np.mean(qam[idx_q]))

    hf_boot = np.array(hf_boot)
    qam_boot = np.array(qam_boot)

    plt.figure(figsize=(8,5))

    plt.hist(
        hf_boot,
        bins=40,
        density=True,
        alpha=0.6,
        label="Hopfield"
    )

    plt.hist(
        qam_boot,
        bins=40,
        density=True,
        alpha=0.6,
        label="QAM"
    )

    plt.axvline(np.mean(hf_boot), linestyle="--")
    plt.axvline(np.mean(qam_boot), linestyle="--")

    plt.xlabel("Bootstrap Mean Full Recall Accuracy")
    plt.ylabel("Density")
    plt.title("Bootstrap Distributions of Mean Full Recall Accuracy")
    plt.legend()

    plt.tight_layout()
    out_path = plots_dir / "bootstrap_full_accuracy_distribution.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
