"""Plot aggregated noise-robustness sweep results."""

import pandas as pd
import matplotlib.pyplot as plt

from src.paths import results_subdir


def finish_plot():
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def main():
    summary_dir = results_subdir("noise_robustness_sweep", "summary")
    plots_dir = results_subdir("noise_robustness_sweep", "plots")
    csv_path = summary_dir / "noise_robustness_sweep.csv"

    df = pd.read_csv(csv_path)

    plt.figure(figsize=(8, 5))

    for n_bits in sorted(df["n_bits"].unique()):

        sub = df[df["n_bits"] == n_bits].sort_values("corruption")

        plt.errorbar(
            sub["corruption"],
            sub["hopfield_full_acc_mean"],
            yerr=sub["hopfield_full_acc_ci"],
            marker="o",
            capsize=3,
            label=f"Hopfield (n={n_bits})"
        )

        plt.errorbar(
            sub["corruption"],
            sub["qam_full_acc_mean"],
            yerr=sub["qam_full_acc_ci"],
            marker="s",
            capsize=3,
            linestyle="--",
            label=f"QAM (n={n_bits})"
        )

    plt.xlabel("Corruption Probability")
    plt.ylabel("Full-Pattern Recall Accuracy")
    plt.title("Full-Pattern Recall Accuracy vs Noise Probability")
    plt.ylim(0, 1.05)
    plt.legend(ncol=2)
    finish_plot()

    plt.savefig(plots_dir / "full_accuracy_vs_noise.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    for n_bits in sorted(df["n_bits"].unique()):

        sub = df[df["n_bits"] == n_bits].sort_values("corruption")

        plt.errorbar(
            sub["corruption"],
            sub["hopfield_bit_acc_mean"],
            yerr=sub["hopfield_bit_acc_ci"],
            marker="o",
            capsize=3,
            label=f"Hopfield (n={n_bits})"
        )

        plt.errorbar(
            sub["corruption"],
            sub["qam_bit_acc_mean"],
            yerr=sub["qam_bit_acc_ci"],
            marker="s",
            capsize=3,
            linestyle="--",
            label=f"QAM (n={n_bits})"
        )

    plt.xlabel("Corruption Probability")
    plt.ylabel("Bitwise Recall Accuracy")
    plt.title("Bitwise Recall Accuracy vs Noise Probability")
    plt.ylim(0, 1.05)
    plt.legend(ncol=2)
    finish_plot()

    plt.savefig(plots_dir / "bitwise_accuracy_vs_noise.png", dpi=300)
    plt.close()

    print("Saved:")
    print(f" - {plots_dir / 'full_accuracy_vs_noise.png'}")
    print(f" - {plots_dir / 'bitwise_accuracy_vs_noise.png'}")


if __name__ == "__main__":
    main()
