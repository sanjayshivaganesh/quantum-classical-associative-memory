"""Plot scaling-sweep trial results."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.paths import results_subdir


def main():
    raw_dir = results_subdir("scaling", "raw")
    plots_dir = results_subdir("scaling", "plots")
    csv_path = raw_dir / "scaling_sweep.csv"

    sns.set_theme(style="whitegrid")

    df = pd.read_csv(csv_path)
    print(df.head())

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="n_bits",
        y="full_acc",
        hue="model",
        style="model",
        markers=True,
        errorbar=("ci", 95)
    )

    plt.title("Full Pattern Retrieval Accuracy vs Pattern Length")
    plt.xlabel("Pattern Length (n_bits)")
    plt.ylabel("Full Retrieval Accuracy")

    plt.tight_layout()

    plt.savefig(plots_dir / "full_accuracy_vs_nbits.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="n_bits",
        y="bit_acc",
        hue="model",
        style="model",
        markers=True,
        errorbar=("ci", 95)
    )

    plt.title("Bitwise Accuracy vs Pattern Length")
    plt.xlabel("Pattern Length (n_bits)")
    plt.ylabel("Bitwise Accuracy")

    plt.tight_layout()

    plt.savefig(plots_dir / "bit_accuracy_vs_nbits.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="noise_p",
        y="full_acc",
        hue="model",
        style="model",
        markers=True,
        errorbar=("ci", 95)
    )

    plt.title("Noise Robustness")
    plt.xlabel("Noise Probability")
    plt.ylabel("Full Retrieval Accuracy")

    plt.tight_layout()

    plt.savefig(plots_dir / "noise_robustness.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="n_bits",
        y="infer_time_s",
        hue="model",
        style="model",
        markers=True,
        errorbar=("ci", 95)
    )

    plt.title("Inference Time Scaling")
    plt.xlabel("Pattern Length (n_bits)")
    plt.ylabel("Inference Time (s)")

    plt.tight_layout()

    plt.savefig(plots_dir / "inference_time_scaling.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="n_bits",
        y="train_time_s",
        hue="model",
        style="model",
        markers=True,
        errorbar=("ci", 95)
    )

    plt.title("Training Time Scaling")
    plt.xlabel("Pattern Length (n_bits)")
    plt.ylabel("Training Time (s)")

    plt.tight_layout()

    plt.savefig(plots_dir / "training_time_scaling.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))

    sns.lineplot(
        data=df,
        x="n_bits",
        y="params_count",
        hue="model",
        style="model",
        markers=True,
        errorbar=None
    )

    plt.title("Parameter Scaling")
    plt.xlabel("Pattern Length (n_bits)")
    plt.ylabel("Parameter Count")

    plt.tight_layout()

    plt.savefig(plots_dir / "parameter_scaling.png", dpi=300)
    plt.close()

    print(f"Plots saved to: {plots_dir}")


if __name__ == "__main__":
    main()
