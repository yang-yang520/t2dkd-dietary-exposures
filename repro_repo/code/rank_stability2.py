# -*- coding: utf-8 -*-
"""§5 SHAP 排名稳定性（国家 bootstrap，适配慢 SHAP 环境）。
   500 棵树（与主分析一致）；SHAP 在每轮 100 行子样本上计算；100 次重复。"""
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
countries = np.unique(groups)
IDX = {c: np.where(groups == c)[0] for c in countries}
print("panel:", X_all.shape, "| countries:", len(countries), flush=True)

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
    ranks = np.argsort(-imps, axis=1).argsort(axis=1) + 1
    df = pd.DataFrame(ranks, columns=[LAB[f] for f in DIET])
    summ = pd.DataFrame({
        "median_rank": df.median().round(1),
        "rank_range": df.min().astype(int).astype(str) + "-" + df.max().astype(int).astype(str),
        "pct_top3": ((df <= 3).mean()*100).round(1),
        "pct_top1": ((df == 1).mean()*100).round(1),
    }).sort_values(["median_rank","pct_top3"], ascending=[True, False])
    summ.to_csv(rf"D:\work\_rank_stability_{out}.csv", encoding="utf-8-sig")
    print(f"\n=== {out}（{NB} 次国家 bootstrap, {time.time()-t0:.0f}s）===", flush=True)
    print(summ.to_string(), flush=True)
print("\nDONE")
