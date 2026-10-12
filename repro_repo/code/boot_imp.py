# -*- coding: utf-8 -*-
"""第7条配套：保存 bootstrap 的 SHAP 重要性数值（不只排名），用于补充材料展示分布。"""
import numpy as np, pandas as pd, warnings, time
warnings.filterwarnings("ignore")
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor
import shap

DIET = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
        "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
LAB = {"sodium_mg":"Dietary sodium","ssb_g":"SSB","unproc_red_meat_g":"Unprocessed red meat",
       "proc_meat_g":"Processed meat","whole_grains_g":"Whole grains","refined_grains_g":"Refined grains",
       "beans_legumes_g":"Beans & legumes","fruits_g":"Fruits"}
p = pd.read_csv(r"D:\work\_panel_sdi.csv").dropna(subset=DIET+["ASIR","DALY_rate"])
X_all = p[DIET].values; groups = p["iso3"].values
countries = np.unique(groups); IDX = {c: np.where(groups == c)[0] for c in countries}

def one(seed, y, nsub=100):
    rng = np.random.RandomState(seed)
    pick = rng.choice(countries, size=len(countries), replace=True)
    rows = np.concatenate([IDX[c] for c in pick])
    rf = RandomForestRegressor(n_estimators=500, max_features=2, random_state=seed, n_jobs=1).fit(X_all[rows], y[rows])
    sub = rng.choice(len(rows), size=min(nsub, len(rows)), replace=False)
    sv = np.asarray(shap.TreeExplainer(rf).shap_values(X_all[rows][sub]))
    if sv.ndim == 3: sv = sv[:, :, 0]
    return np.abs(sv).mean(axis=0)

NB = 100
for out in ["ASIR","DALY_rate"]:
    y = p[out].values; t0 = time.time()
    imps = np.array(Parallel(n_jobs=6)(delayed(one)(123+i, y) for i in range(NB)))
    df = pd.DataFrame(imps, columns=[LAB[f] for f in DIET])
    df.to_csv(rf"D:\work\_boot_shap_imp_{out}.csv", index=False, encoding="utf-8-sig")
    summ = pd.DataFrame({
        "median_meanSHAP": df.median().round(3),
        "p2.5": df.quantile(0.025).round(3),
        "p97.5": df.quantile(0.975).round(3),
    }).sort_values("median_meanSHAP", ascending=False)
    print(f"\n=== {out}（{NB} 次 bootstrap, {time.time()-t0:.0f}s） mean|SHAP| 分布 ===", flush=True)
    print(summ.to_string(), flush=True)
print("\nDONE")
