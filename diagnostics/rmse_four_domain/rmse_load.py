"""DIAGNOSTIC. Exact logic of experiments/uci_energy_lightgbm.py (expanding window, 14 lags + i%7), also recording RMSE."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
from lightgbm import LGBMRegressor
from multiprocessing import Pool
ROOT=Path("/home/fede/repos/paper2H"); OUT=ROOT/"diagnostics/rmse_four_domain"
MAX_LAG=14; TW=365
df=pd.read_csv(ROOT/"results/uci_electricity_daily_aggregate.csv",parse_dates=["timestamp"]).sort_values("timestamp")
y=df["value"].values; n=len(y)
cols=[f"lag_{i}" for i in range(1,MAX_LAG+1)]+["day_of_week"]
def one(h):
    em=[];eb=[]
    for t in range(TW,n-h):
        if t<MAX_LAG: continue
        rows=[]
        for i in range(MAX_LAG,t-h+1):
            r=[y[i-l] for l in range(1,MAX_LAG+1)]; r.append(i%7); r.append(y[i+h-1]); rows.append(r)
        if len(rows)<10: continue
        d=pd.DataFrame(rows,columns=cols+["target"])
        xt={f"lag_{l}":y[t-l] for l in range(1,MAX_LAG+1)}; xt["day_of_week"]=t%7
        m=LGBMRegressor(n_estimators=100,learning_rate=0.05,num_leaves=15,random_state=42,verbosity=-1,n_jobs=1)
        m.fit(d[cols],d["target"].values)
        p=float(m.predict(pd.DataFrame([xt],columns=cols))[0]); b=float(y[t-1]); yt=float(y[t+h-1])
        em.append(yt-p); eb.append(yt-b)
    em=np.array(em);eb=np.array(eb)
    return dict(horizon=h,baseline_mae=np.abs(eb).mean(),model_mae=np.abs(em).mean(),n=len(em),
                baseline_rmse=np.sqrt((eb**2).mean()),model_rmse=np.sqrt((em**2).mean()))
if __name__=="__main__":
    with Pool(7) as p: rows=p.map(one,range(1,8))
    pd.DataFrame(rows).to_csv(OUT/"load_mae_rmse.csv",index=False); print("load done")
