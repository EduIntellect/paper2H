"""DIAGNOSTIC ONLY. Order selection (auto_arima AIC, d=0, with intercept) at 20 evenly spaced
valid pipeline-A origins per domain (h=1). Output: order_stability.csv"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, pmdarima as pm
from statsmodels.tsa.stattools import adfuller
import arima_order_diagnostic as D
rows=[]
for dom in ("wind","traffic"):
    cfg=D.CFG[dom]; s,_=D.load(cfg["path"]); n=len(s)
    origins=list(range(48,n-2+1,24))[-cfg["n_origins"]:]
    valid=[o for o in origins if o-1>=48 and len(D.window(s,o)[0])>=200]
    pick=[valid[i] for i in np.linspace(0,len(valid)-1,20).round().astype(int)]
    for o in pick:
        y=D.window(s,o)[0]
        fits=pm.auto_arima(y,seasonal=False,d=0,max_p=5,max_q=5,stepwise=False,suppress_warnings=True,
                           error_action="ignore",return_valid_fits=True,n_jobs=1,maxiter=1000,with_intercept=True)
        r=sorted(((f.order,f.aic()) for f in fits),key=lambda t:t[1])
        a200=dict(r)[(2,0,0)]
        rows.append(dict(domain=dom,origin=o,n_train=len(y),best_order=str(r[0][0]),best_aic=r[0][1],
            aic_200=a200,delta_aic_200=a200-r[0][1],rank_200=[x[0] for x in r].index((2,0,0))+1,
            n_models=len(r),adf_p=adfuller(y.values,autolag="AIC")[1]))
df=pd.DataFrame(rows); df.to_csv("order_stability.csv",index=False)
pd.set_option("display.width",200)
print(df.round(3).to_string(index=False))
for d,g in df.groupby("domain"):
    print(f"\n{d}: best_order counts ->",g.best_order.value_counts().to_dict())
    print(f"  delta_AIC(2,0,0)-best: median={g.delta_aic_200.median():.2f} max={g.delta_aic_200.max():.2f}; "
          f"rank(2,0,0): median={g['rank_200'].median():.0f}, in top3={(g['rank_200']<=3).sum()}/20, "
          f"within dAIC<=2: {(g.delta_aic_200<=2).sum()}/20; ADF p>0.05: {(g.adf_p>0.05).sum()}/20")
