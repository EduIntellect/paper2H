"""DIAGNOSTIC. Re-run the four-domain LightGBM producers (wind, traffic, pm25_full) unchanged, only
recording RMSE next to MAE by wrapping sklearn's mean_absolute_error. Writes only to this dir."""
import sys, os, warnings
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import Pool
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path("/home/fede/repos/paper2H"); OUT=ROOT/"diagnostics/rmse_four_domain"
CFG={"wind":("wind_predictability.py","load_wind_series",range(1,49)),
     "traffic":("traffic_predictability.py","load_traffic_series",range(1,73)),
     "pm25":("pm25_lightgbm_full.py","load_real_pm25",range(1,49))}
def one(args):
    dom,h=args; os.chdir(ROOT); warnings.filterwarnings("ignore")
    f,loader,_=CFG[dom]
    spec=spec_from_file_location("m",ROOT/"experiments"/f); m=module_from_spec(spec); spec.loader.exec_module(m)
    rec=[]; orig=m.mean_absolute_error
    def patched(yt,yp):
        rec.append((len(yt),float(np.sqrt(np.mean((np.asarray(yt)-np.asarray(yp))**2))))); return orig(yt,yp)
    m.mean_absolute_error=patched
    s=getattr(m,loader)(m.DATA_PATH)
    res=m.evaluate_rolling_origin_lightgbm(series=s,horizons=[h],lags=m.LAGS); b,mo=res[1],res[2]
    return dict(horizon=h,baseline_mae=float(b[0]),model_mae=float(mo[0]),n=rec[0][0] if rec else 0,
                baseline_rmse=rec[0][1] if rec else np.nan,model_rmse=rec[1][1] if len(rec)>1 else np.nan)
if __name__=="__main__":
    dom=sys.argv[1]; nproc=int(sys.argv[2])
    with Pool(nproc) as p: rows=p.map(one,[(dom,h) for h in CFG[dom][2]],chunksize=1)
    pd.DataFrame(sorted(rows,key=lambda r:r["horizon"])).to_csv(OUT/f"{dom}_mae_rmse.csv",index=False); print(dom,"done")
