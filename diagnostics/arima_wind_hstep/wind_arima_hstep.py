"""DIAGNOSTIC RERUN. Wind ARIMA(2,0,0) with a true h-step forecast (steps=h), everything else identical
to experiments/wind_arima_canonical_predictability.py (same evaluator, windows, origins, order).
Writes only to diagnostics/arima_wind_hstep/. Run from repo root."""
import sys, warnings
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
from statsmodels.tsa.arima.model import ARIMA

ROOT = Path("/home/fede/repos/paper2H"); OUT = ROOT / "diagnostics" / "arima_wind_hstep"
ORDER = (2, 0, 0)

class Adapter:
    def __init__(self, horizon=1, **kw): self.h = horizon; self._f = None
    def fit(self, X, y):
        y = pd.Series(y).dropna().astype(float)
        if len(y) < 10: raise ValueError("too short")
        y.index = pd.date_range("2000-01-01", periods=len(y), freq="h")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore"); self._f = ARIMA(y, order=ORDER).fit()
        return self
    def predict(self, X):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore"); return np.array([float(self._f.forecast(steps=self.h).iloc[-1])])

def one(h):
    import os; os.chdir(ROOT); warnings.filterwarnings("ignore")
    spec = spec_from_file_location("wp", ROOT / "experiments/wind_predictability.py")
    m = module_from_spec(spec); spec.loader.exec_module(m)
    m.LGBMRegressor = lambda **kw: Adapter(horizon=h, **kw)
    s = m.load_wind_series(m.DATA_PATH)
    _, b, mo = m.evaluate_rolling_origin_lightgbm(series=s, horizons=[h], lags=m.LAGS)
    return h, float(b[0]), float(mo[0])

if __name__ == "__main__":
    hs = list(range(1, 49))
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as p:
        res = sorted(p.map(one, hs, chunksize=1))
    df = pd.DataFrame(res, columns=["horizon", "baseline_mae", "model_mae"])
    df["skill"] = 1 - df.model_mae / df.baseline_mae
    df.to_csv(OUT / "wind_arima_hstep_errors.csv", index=False)
    print(df.to_string(index=False))
