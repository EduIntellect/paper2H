"""Paper figures: ACF/PACF of the last evaluated h=1 training window (pipeline A), one figure per domain."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import arima_order_diagnostic as D
OUT = D.REPO / "revision/overleaf_2026-10-01/submission"
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10})
for dom in ("wind", "traffic"):
    s, _ = D.load(D.CFG[dom]["path"]); n = len(s)
    origins = list(range(48, n - 2 + 1, 24))[-D.CFG[dom]["n_origins"]:]
    valid = [o for o in origins if o - 1 >= 48 and len(D.window(s, o)[0]) >= 200]
    y = D.window(s, valid[-1])[0].values
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    plot_acf(y, lags=48, ax=ax[0], title="ACF")
    plot_pacf(y, lags=48, method="ywm", ax=ax[1], title="PACF")
    for a in ax:
        a.set_xlabel("Lag (hours)"); a.set_ylim(-0.4, 1.05); a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / f"fig_acf_pacf_{dom}.pdf")
    print(dom, "origin", valid[-1], "n", len(y))
