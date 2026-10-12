# -*- coding: utf-8 -*-
"""第八条（上一轮）重做：国家层面「整条轨迹」置换零模型。
   每个国家把其 7 年的完整结局轨迹整体换给另一个国家（保留国家内序列），再跑同一 GroupKFold。"""
import numpy as np, pandas as pd, warnings, time
warnings.filterwarnings("ignore")
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score

DIET = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
        "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
p = pd.read_csv(r"D:\work\_panel_sdi.csv").dropna(subset=DIET+["ASIR","DALY_rate"])
X = p[DIET].values; groups = p["iso3"].values
countries = np.unique(groups)
IDX = {c: np.where(groups == c)[0] for c in countries}
SPLITS = list(GroupKFold(n_splits=5).split(X, np.zeros(len(X)), groups))
print("panel:", X.shape, "| countries:", len(countries), flush=True)

def cv_r2(y):
    def fit(tr, te):
        m = RandomForestRegressor(n_estimators=500, max_features=2, random_state=123, n_jobs=1).fit(X[tr], y[tr])
        return te, m.predict(X[te])
    res = Parallel(n_jobs=-1)(delayed(fit)(tr, te) for tr, te in SPLITS)
    oof = np.zeros(len(y))
    for te, pr in res: oof[te] = pr
    return r2_score(y, oof)

NPERM = 100
for out in ["ASIR","DALY_rate"]:
    y = p[out].values; t0 = time.time()
    obs = cv_r2(y)
    def perm_r2(seed):
        rng = np.random.RandomState(seed)
        src = rng.permutation(len(countries))      # 国家 i 拿到国家 src[i] 的整条轨迹
        yp = np.empty_like(y)
        for i, c in enumerate(countries):
            yp[IDX[c]] = y[IDX[countries[src[i]]]]
        return cv_r2(yp)
    null = np.array(Parallel(n_jobs=-1)(delayed(perm_r2)(999+i) for i in range(NPERM)))
    pval = (np.sum(null >= obs) + 1) / (NPERM + 1)
    print(f"\n=== {out}（{NPERM} 次国家轨迹置换, {time.time()-t0:.0f}s）===", flush=True)
    print(f"  observed R2 = {obs:.4f}", flush=True)
    print(f"  null: median={np.median(null):.4f} p95={np.quantile(null,0.95):.4f} max={null.max():.4f}", flush=True)
    print(f"  empirical p = {pval:.3f}", flush=True)
    pd.DataFrame({"null_R2": null}).to_csv(rf"D:\work\_perm_null2_{out}.csv", index=False, encoding="utf-8-sig")
print("\nDONE")
