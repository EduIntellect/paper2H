"""DIAGNOSTIC ONLY. Reconstructs the pipeline-A training window (h=1) at the first
and last evaluated origin and runs ACF/PACF, ADF and auto_arima (AIC).
Does not import or modify any production script."""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pmdarima as pm

warnings.filterwarnings("ignore")
REPO = Path("/home/fede/repos/paper2H")
OUT = REPO / "diagnostics" / "arima_order"

# Constants copied from experiments/{wind,traffic}_predictability.py
CFG = {
    "wind": dict(path="data/wind_hourly_clean.csv", n_origins=365),
    "traffic": dict(path="data/traffic_hourly_clean.csv", n_origins=180),
}
LAGS = [0, 1, 2, 3, 6, 12, 24, 48]
STRIDE, MAX_TRAIN = 24, 24 * 30
H = 1


def load(path):  # same as load_*_series
    df = pd.read_csv(REPO / path, parse_dates=["timestamp"]).sort_values("timestamp")
    s = pd.to_numeric(df["value"], errors="coerce")
    return s.interpolate(method="linear", limit_direction="both").reset_index(drop=True), df


def window(series, origin, h=H):
    max_lag = max(LAGS)
    target = series.shift(-h)
    train_end = origin - h
    train_start = max(max_lag, train_end - MAX_TRAIN + 1)
    idx = np.arange(train_start, train_end + 1)
    lag_ok = pd.concat([series.shift(l) for l in LAGS], axis=1).iloc[idx].notna().all(axis=1)
    y = target.iloc[idx]
    mask = lag_ok & y.notna()
    return y.loc[mask], train_start, train_end


def top_fits(y, label, **kw):
    fits = pm.auto_arima(y, seasonal=False, information_criterion="aic", max_p=5, max_q=5,
                         max_d=2, stepwise=False, suppress_warnings=True, error_action="ignore",
                         return_valid_fits=True, n_jobs=1, maxiter=1000, with_intercept=True, **kw)
    rows = sorted(((f.order, f.aic()) for f in fits), key=lambda t: t[1])
    print(f"  [{label}] models fitted: {len(rows)}")
    for i, (o, a) in enumerate(rows[:4]):
        print(f"    {'BEST ' if i == 0 else f'#{i+1}   '} order={o}  AIC={a:.3f}")
    ref = pm.ARIMA(order=(2, 0, 0), suppress_warnings=True).fit(y)
    rank = [o for o, _ in rows].index((2, 0, 0)) + 1 if (2, 0, 0) in [o for o, _ in rows] else None
    print(f"    (2,0,0) with const (same engine): AIC={ref.aic():.3f}  rank_in_list={rank}")
    return rows, ref.aic()


def run(domain, which):
    cfg = CFG[domain]
    series, df = load(cfg["path"])
    n = len(series)
    origins = list(range(max(LAGS), n - H - 1 + 1, STRIDE))[-cfg["n_origins"]:]
    # same validity filters as A: train_end>=max_lag and >=200 valid train samples
    valid = []
    for o in origins:
        if o - H < max(LAGS):
            continue
        yy, _, _ = window(series, o)
        if len(yy) >= 200:
            valid.append(o)
    print(f"\n[{domain}] candidates={len(origins)} (first={origins[0]}, last={origins[-1]}), "
          f"valid under A filters={len(valid)} (first={valid[0]}, last={valid[-1]})")
    origin = valid[0] if which == "first" else valid[-1]
    y, ts, te = window(series, origin)
    stamp = df["timestamp"].reset_index(drop=True)
    print(f"\n{'='*78}\n{domain.upper()} / {which} origin  (n={n}, n_origins={len(origins)}, "
          f"origin_idx={origin}, h={H})")
    print(f"  train idx [{ts}..{te}] -> y_train = series[{ts+H}..{te+H}], len={len(y)}")
    print(f"  y_train timestamps: {stamp[ts+H]} .. {stamp[te+H]}")
    print(f"  mean={y.mean():.4f} std={y.std():.4f} min={y.min():.4f} max={y.max():.4f}")

    nl = 48
    a = acf(y.values, nlags=nl, fft=True)
    p = pacf(y.values, nlags=nl, method="ywm")
    print("  lag   ACF      PACF")
    for k in range(1, 11):
        print(f"  {k:>3}  {a[k]:+.4f}  {p[k]:+.4f}")
    print(f"  (95% band ±{1.96/np.sqrt(len(y)):.4f}); lag24 ACF={a[24]:+.4f} PACF={p[24]:+.4f}; "
          f"lag48 ACF={a[48]:+.4f} PACF={p[48]:+.4f}")

    adf = adfuller(y.values, autolag="AIC")
    print(f"  ADF: stat={adf[0]:.4f} p={adf[1]:.4g} usedlag={adf[2]} nobs={adf[3]} "
          f"crit={ {k: round(v,3) for k,v in adf[4].items()} }")

    fig, ax = plt.subplots(2, 1, figsize=(9, 6))
    plot_acf(y.values, lags=nl, ax=ax[0], title=f"{domain} {which} origin ({origin}) ACF")
    plot_pacf(y.values, lags=nl, method="ywm", ax=ax[1], title=f"{domain} {which} origin PACF")
    fig.tight_layout()
    fig.savefig(OUT / f"{domain}_{which}_acf_pacf.png", dpi=130)
    plt.close(fig)

    print("  -- auto_arima AIC, d free (KPSS-chosen), p,q<=5, d<=2")
    top_fits(y, "d free")
    print("  -- auto_arima AIC, d=0 fixed, p,q<=5")
    top_fits(y, "d=0", d=0)


if __name__ == "__main__":
    for dom in ("wind", "traffic"):
        for w in ("first", "last"):
            run(dom, w)
