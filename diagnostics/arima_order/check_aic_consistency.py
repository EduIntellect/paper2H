import warnings; warnings.filterwarnings("ignore")
import numpy as np, pmdarima as pm
from statsmodels.tsa.arima.model import ARIMA as SMARIMA
import arima_order_diagnostic as D
for dom,which in [("wind","first"),("traffic","first"),("wind","last"),("traffic","last")]:
    cfg=D.CFG[dom]; s,_=D.load(cfg["path"]); n=len(s)
    origins=list(range(48,n-2+1,24))[-cfg["n_origins"]:]
    valid=[o for o in origins if o-1>=48 and len(D.window(s,o)[0])>=200]
    o=valid[0] if which=="first" else valid[-1]
    y=D.window(s,o)[0]
    fits=pm.auto_arima(y,seasonal=False,d=0,max_p=5,max_q=5,stepwise=False,suppress_warnings=True,error_action="ignore",return_valid_fits=True,n_jobs=1,maxiter=1000,with_intercept=True)
    inlist={f.order:f.aic() for f in fits}.get((2,0,0))
    direct=pm.ARIMA(order=(2,0,0)).fit(y).aic()
    sm=SMARIMA(y.values,order=(2,0,0),trend="c").fit()
    print(dom,which,"(2,0,0) AIC: in auto_arima list=",inlist,"| pm.ARIMA direct=",round(direct,3),"| statsmodels ARIMA trend=c =",round(sm.aic,3))
