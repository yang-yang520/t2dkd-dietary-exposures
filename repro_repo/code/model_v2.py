# -*- coding: utf-8 -*-
"""阶段2 核心建模（重构版，joblib 并行）：
主分析=RF回归(连续 ASIR/DALY_rate)；验证=GroupKFold + LOCO(留一国家)；重要性=SHAP为主+置换为辅；
敏感性=4分类 + 5/10年 lag。漏洞：B1泄漏→分组CV、B2离散化→回归、B3主指标=SHAP、A3滞后。
"""
import pandas as pd, numpy as np, warnings, time
warnings.filterwarnings("ignore")
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.inspection import permutation_importance
from sklearn.metrics import (r2_score, mean_squared_error, mean_absolute_error,
                             accuracy_score, f1_score, cohen_kappa_score)
import shap

np.random.seed(123)

FEATURES = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
            "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
LABELS = {
    "sodium_mg":"Dietary sodium","ssb_g":"SSB","unproc_red_meat_g":"Unprocessed red meat",
    "proc_meat_g":"Processed meat","whole_grains_g":"Whole grains","refined_grains_g":"Refined grains",
    "beans_legumes_g":"Beans & legumes","fruits_g":"Fruits",
}
LABEL_LIST = [LABELS[f] for f in FEATURES]

panel = pd.read_csv(r"D:\work\_panel.csv").dropna(subset=FEATURES+["ASIR","DALY_rate"])
X = panel[FEATURES].values
groups = panel["iso3"].values
print(f"panel: {panel.shape[0]} rows, {panel['iso3'].nunique()} countries, {sorted(panel.year.unique())}", flush=True)

def _fit_one(X, y, tr, te, clf):
    m = (RandomForestClassifier if clf else RandomForestRegressor)(
        n_estimators=500, max_features=2, random_state=123, n_jobs=1)
    m.fit(X[tr], y[tr])
    return te, m.predict(X[te])

def oof_predict(X, y, groups, cv, clf):
    splits = list(cv.split(X, y, groups))
    res = Parallel(n_jobs=-1)(delayed(_fit_one)(X, y, tr, te, clf) for tr, te in splits)
    oof = np.zeros(len(y), dtype=object if clf else float)
    for te, pred in res:
        oof[te] = pred
    return oof

def cv_reg(X, y, groups):
    oof = oof_predict(X, y, groups, GroupKFold(n_splits=5), False)
    res = dict(R2_GK=round(r2_score(y, oof),4), RMSE_GK=round(float(np.sqrt(mean_squared_error(y, oof))),2),
               MAE_GK=round(mean_absolute_error(y, oof),2),
               R2log_GK=round(r2_score(np.log(np.clip(y,1e-9,None)), np.log(np.clip(oof,1e-9,None))),4))
    oof2 = oof_predict(X, y, groups, LeaveOneGroupOut(), False)
    res.update(R2_LOCO=round(r2_score(y, oof2),4), RMSE_LOCO=round(float(np.sqrt(mean_squared_error(y, oof2))),2),
               MAE_LOCO=round(mean_absolute_error(y, oof2),2))
    return res

def cv_clf(X, y, groups):
    oof = oof_predict(X, y, groups, GroupKFold(n_splits=5), True)
    res = dict(acc_GK=round(accuracy_score(y, oof),4), f1_GK=round(f1_score(y, oof, average="macro"),4),
               kappa_GK=round(cohen_kappa_score(y, oof),4))
    oof2 = oof_predict(X, y, groups, LeaveOneGroupOut(), True)
    res.update(acc_LOCO=round(accuracy_score(y, oof2),4), f1_LOCO=round(f1_score(y, oof2, average="macro"),4),
               kappa_LOCO=round(cohen_kappa_score(y, oof2),4))
    return res

def fit_reg(X, y):
    return RandomForestRegressor(n_estimators=500, max_features=2, random_state=123, n_jobs=-1).fit(X, y)

def importance(X, y, tag, do_perm=True):
    rf = fit_reg(X, y)
    sv = np.asarray(shap.TreeExplainer(rf).shap_values(X))
    shap_imp = pd.DataFrame({"feature":LABEL_LIST, "mean_abs_shap":np.abs(sv).mean(axis=0)}
                            ).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    perm_imp = None
    if do_perm:
        perm = permutation_importance(rf, X, y, scoring="r2", n_repeats=10, random_state=123, n_jobs=-1)
        perm_imp = pd.DataFrame({"feature":LABEL_LIST, "mean_r2_decrease":perm.importances_mean,
                                 "std":perm.importances_std}
                                ).sort_values("mean_r2_decrease", ascending=False).reset_index(drop=True)
        perm_imp.to_csv(rf"D:\work\_reg_perm_{tag}.csv", index=False)
    shap_imp.to_csv(rf"D:\work\_reg_shap_{tag}.csv", index=False)
    return shap_imp, perm_imp

def lag_panel(gap):
    years = [1990,1995,2000,2005,2010,2015,2018]
    rows = []
    for t in years:
        if t+gap in years:
            diet = panel[panel.year==t].copy()
            burd = panel[panel.year==t+gap][["location_name","ASIR","DALY_rate"]].rename(
                columns={"ASIR":"ASIR_lag","DALY_rate":"DALY_rate_lag"})
            m = diet.merge(burd, on="location_name").dropna(subset=FEATURES+["ASIR_lag","DALY_rate_lag"])
            rows.append(m)
    return pd.concat(rows).reset_index(drop=True)

t0 = time.time()
print("\n===== 回归（主分析）=====", flush=True)
for col, name in [("ASIR","ASIR"), ("DALY_rate","DALY")]:
    res = cv_reg(X, panel[col].values, groups)
    print(f"{name}: " + ", ".join(f"{k}={v}" for k,v in res.items()), flush=True)

print("\n===== 分类（敏感性，与原手稿口径对比）=====", flush=True)
for col, name in [("ASIR_cat","ASIR"), ("DALY_cat","DALY")]:
    res = cv_clf(X, panel[col].values, groups)
    print(f"{name}: " + ", ".join(f"{k}={v}" for k,v in res.items()), flush=True)

print("\n===== 重要性（回归，SHAP 为主 + 置换为辅）=====", flush=True)
for col, name in [("ASIR","ASIR"), ("DALY_rate","DALY")]:
    shap_imp, perm_imp = importance(X, panel[col].values, name)
    print(f"\n[{name}] SHAP mean|SHAP| 排名:", flush=True)
    for _, r in shap_imp.iterrows():
        print(f"   {r['feature']:22s} {r['mean_abs_shap']:.4f}", flush=True)
    if perm_imp is not None:
        print(f"[{name}] 置换重要性(R2下降) 排名:", flush=True)
        for _, r in perm_imp.iterrows():
            print(f"   {r['feature']:22s} {r['mean_r2_decrease']:.4f} ± {r['std']:.4f}", flush=True)

print("\n===== 滞后敏感性（lag）=====", flush=True)
for gap in [5, 10]:
    lp = lag_panel(gap)
    print(f"\n--- {gap} 年 lag：diet(t) -> burden(t+{gap})，n={len(lp)} ---", flush=True)
    for col, name in [("ASIR_lag","ASIR"), ("DALY_rate_lag","DALY")]:
        shap_imp, _ = importance(lp[FEATURES].values, lp[col].values, f"{name}_lag{gap}", do_perm=False)
        print(f"  {name}: top3 = {shap_imp['feature'].head(3).tolist()}", flush=True)

print(f"\nDONE in {time.time()-t0:.0f}s", flush=True)
