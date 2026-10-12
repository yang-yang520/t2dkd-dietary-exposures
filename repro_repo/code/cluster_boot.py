# -*- coding: utf-8 -*-
"""第5条核实：lead-lag 740 条观测的国家内相关性。
   对红肉→ASIR 的 Spearman 相关，用【国家聚类 bootstrap】重算稳健 p 值与 95% CI。"""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from scipy import stats

FEATURES = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g",
            "whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
panel = pd.read_csv(r"D:\work\_panel.csv").dropna(subset=FEATURES+["ASIR","DALY_rate"])

# 复现原始 lead-lag 数据（国家内，Δ膳食(t-5→t) vs Δ负担(t→t+5)）
piv = {f: panel.pivot_table(index="iso3", columns="year", values=f) for f in FEATURES}
pB = {o: panel.pivot_table(index="iso3", columns="year", values=o) for o in ["ASIR","DALY_rate"]}

def build_lag(diet_piv, burden_piv):
    rows = []
    for t in [1995, 2000, 2005, 2010]:
        if (t-5) in diet_piv.columns and t in diet_piv.columns and (t+5) in burden_piv.columns:
            dD = diet_piv[t] - diet_piv[t-5]
            dB = burden_piv[t+5] - burden_piv[t]
            m = pd.concat([dD, dB], axis=1).dropna()
            m.columns = ["dD","dB"]; m["iso3"] = m.index
            rows.append(m)
    return pd.concat(rows)

m = build_lag(piv["unproc_red_meat_g"], pB["ASIR"])
print("总观测数 n =", len(m), "| 国家数 =", m.iso3.nunique())

# ① 原始（把每条当独立）的 Spearman
r0, p0 = stats.spearmanr(m["dD"], m["dB"])
print(f"原始（忽略聚类）: ρ={r0:.3f}, p={p0:.6f}")

# ② 国家聚类 bootstrap
countries = m.iso3.unique()
groups = {c: m[m.iso3==c] for c in countries}
rng = np.random.RandomState(123)
NB = 2000
rs = []
for i in range(NB):
    pick = rng.choice(countries, size=len(countries), replace=True)
    sub = pd.concat([groups[c] for c in pick])
    r, _ = stats.spearmanr(sub["dD"], sub["dB"])
    rs.append(r)
rs = np.array(rs)
ci = np.percentile(rs, [2.5, 97.5])
# 稳健 p 值：零假设下 ρ=0，看 bootstrap 分布中 |ρ| 超过 |r0| 的比例（双尾）
# 更稳妥：用 bootstrap 分布的符号检验；这里用中心化后的分布
centered = rs - rs.mean() + 0.0  # 已中心化
p_clustered = float((np.abs(rs) >= np.abs(r0)).mean())
print(f"聚类 bootstrap（{NB} 次, 按国家重抽样）:")
print(f"  ρ 均值 = {rs.mean():.3f}  95% CI = [{ci[0]:.3f}, {ci[1]:.3f}]")
print(f"  稳健 p（|ρ|≥|观测ρ| 比例）≈ {p_clustered:.4f}")
