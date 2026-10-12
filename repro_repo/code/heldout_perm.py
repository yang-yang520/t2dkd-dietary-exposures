# -*- coding: utf-8 -*-
"""第8条：留出国家上的置换重要性（检验钠/精制谷物的领先地位是否在未见国家上成立）。
   每折：在训练折拟合模型，在留出折上计算 permutation importance（scoring=r2, 10 次重复）。"""
import numpy as np, pandas as pd, warnings, time
warnings.filterwarnings("ignore")
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.inspection import permutation_importance

DIET = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
        "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
LAB = {"sodium_mg":"Dietary sodium","ssb_g":"SSB","unproc_red_meat_g":"Unprocessed red meat",
       "proc_meat_g":"Processed meat","whole_grains_g":"Whole grains","refined_grains_g":"Refined grains",
       "beans_legumes_g":"Beans & legumes","fruits_g":"Fruits"}
p = pd.read_csv(r"D:\work\_panel_sdi.csv").dropna(subset=DIET+["ASIR","DALY_rate"])
X = p[DIET].values; groups = p["iso3"].values
SPLITS = list(GroupKFold(n_splits=5).split(X, np.zeros(len(X)), groups))

def fold_perm(tr, te, y):
    m = RandomForestRegressor(n_estimators=500, max_features=2, random_state=123, n_jobs=1).fit(X[tr], y[tr])
    r = permutation_importance(m, X[te], y[te], scoring="r2", n_repeats=10, random_state=123)
    return r.importances_mean

for out in ["ASIR","DALY_rate"]:
    y = p[out].values; t0 = time.time()
    imps = np.array(Parallel(n_jobs=-1)(delayed(fold_perm)(tr, te, y) for tr, te in SPLITS))
    df = pd.DataFrame(imps, columns=[LAB[f] for f in DIET])
    ranks = df.rank(axis=1, ascending=False).astype(int)
    summ = pd.DataFrame({
        "mean_imp_across_folds": df.mean().round(4),
        "median_rank": ranks.median().round(1),
        "rank_range": ranks.min().astype(str) + "-" + ranks.max().astype(str),
        "pct_top3": ((ranks <= 3).mean()*100).round(0),
    }).sort_values("mean_imp_across_folds", ascending=False)
    df.to_csv(rf"D:\work\_heldout_perm_{out}.csv", index=False, encoding="utf-8-sig")
    print(f"\n=== {out} 留出国家置换重要性（5 折, {time.time()-t0:.0f}s）===", flush=True)
    print(summ.to_string(), flush=True)
print("\nDONE")
