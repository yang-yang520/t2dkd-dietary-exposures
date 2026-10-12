# -*- coding: utf-8 -*-
"""重算「按国家分组 CV」的诚实性能指标（回归 + 分类），存 _honest_metrics.csv。"""
import pandas as pd, numpy as np, warnings, time, json
warnings.filterwarnings("ignore")
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.metrics import (r2_score, mean_squared_error, mean_absolute_error,
                             accuracy_score, f1_score, cohen_kappa_score)

np.random.seed(123)
FEATURES = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
            "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]

panel = pd.read_csv(r"D:\work\_panel.csv").dropna(subset=FEATURES+["ASIR","DALY_rate"])
X = panel[FEATURES].values; groups = panel["iso3"].values
print(f"panel rows={len(panel)} countries={panel.iso3.nunique()} years={sorted(panel.year.unique())}", flush=True)

def _fit(X, y, tr, te, clf):
    m = (RandomForestClassifier if clf else RandomForestRegressor)(
        n_estimators=500, max_features=2, random_state=123, n_jobs=1)
    m.fit(X[tr], y[tr]); return te, m.predict(X[te])

def oof(X, y, cv, clf):
    res = Parallel(n_jobs=-1)(delayed(_fit)(X, y, tr, te, clf) for tr, te in cv.split(X, y, groups))
    out = np.zeros(len(y), dtype=object if clf else float)
    for te, p in res: out[te] = p
    return out

rows = []
t0 = time.time()
for col, name in [("ASIR","ASIR"), ("DALY_rate","DALY")]:
    yv = panel[col].values
    for cvname, cv in [("GroupKFold", GroupKFold(n_splits=5)), ("LOCO", LeaveOneGroupOut())]:
        o = oof(X, yv, cv, False)
        d = dict(target=name, cv=cvname,
                 R2=round(r2_score(yv, o),4),
                 RMSE=round(float(np.sqrt(mean_squared_error(yv, o))),2),
                 MAE=round(mean_absolute_error(yv, o),2))
        if cvname == "GroupKFold":
            d["R2_log"] = round(r2_score(np.log(np.clip(yv,1e-9,None)), np.log(np.clip(o,1e-9,None))),4)
        rows.append(d)
        print(f"REG {name} {cvname}: R2={d['R2']} RMSE={d['RMSE']}", flush=True)
for col, name in [("ASIR_cat","ASIR"), ("DALY_cat","DALY")]:
    for cvname, cv in [("GroupKFold", GroupKFold(n_splits=5)), ("LOCO", LeaveOneGroupOut())]:
        o = oof(X, panel[col].values, cv, True)
        rows.append(dict(target=name, cv=cvname,
                         acc=round(accuracy_score(panel[col].values, o),4),
                         f1=round(f1_score(panel[col].values, o, average="macro"),4),
                         kappa=round(cohen_kappa_score(panel[col].values, o),4)))
        print(f"CLF {name} {cvname}: acc={rows[-1]['acc']} f1={rows[-1]['f1']} kappa={rows[-1]['kappa']}", flush=True)

pd.DataFrame(rows).to_csv(r"D:\work\_honest_metrics.csv", index=False, encoding="utf-8-sig")
print(f"DONE {time.time()-t0:.0f}s")
