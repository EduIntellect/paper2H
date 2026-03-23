from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_CSV = Path("results/traffic_skill.csv")
OUTPUT_PDF = Path("figures/fig_skill_traffic.pdf")
OUTPUT_PNG = Path("figures/fig_skill_traffic.png")


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    if not {"horizon", "skill"}.issubset(df.columns):
        raise ValueError("Input must contain columns: horizon, skill")

    x = pd.to_numeric(df["horizon"], errors="raise")
    y = pd.to_numeric(df["skill"], errors="raise")

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(6.2, 3.8))

    ax.plot(x, y, color="black", linewidth=1.8)
    ax.axhline(0.0, color="0.5", linewidth=1.0, linestyle="--")

    ax.set_xlabel("Forecast horizon h")
    ax.set_ylabel("Skill(h)")
    ax.set_xlim(x.min(), x.max())
    ax.margins(x=0.01)

    fig.tight_layout()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PDF, bbox_inches="tight")
    fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
