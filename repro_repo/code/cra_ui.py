# -*- coding: utf-8 -*-
"""① 归因加 95% UI：6-risk 合计可归因率 / PAF / 推导总负担率，含区间。
   UI 用 6 个风险的 lower/upper 分别相加（近似；因风险 UI 相关，属保守上界）。
   推导总负担率 = 可归因率 / PAF；其区间 = (attr_lo/paf_hi, attr_hi/paf_lo)（保守）。
"""
import pandas as pd, numpy as np

m = pd.read_csv(r"D:\work\_cra_master_long.csv")
AS = m[m.age == "AS"]
SDI = ["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
REG = ["Sub-Saharan Africa","North Africa and Middle East","South Asia",
       "Southeast Asia, East Asia, and Oceania",
       "Central Europe, Eastern Europe, and Central Asia","Latin America and Caribbean","High-income"]
LOCS = SDI + ["Global"] + REG

def agg(loc, year):
    r = AS[(AS.location==loc)&(AS.year==year)&(AS.measure=="DALY")]
    attr = r[r.metric=="rate"]; paf = r[r.metric=="paf"]
    if len(attr)==0 or len(paf)==0: return None
    A, Alo, Ahi = attr.val.sum(), attr.lower.sum(), attr.upper.sum()
    P, Plo, Phi = paf.val.sum(), paf.lower.sum(), paf.upper.sum()
    return dict(attr=A, attr_lo=Alo, attr_hi=Ahi,
                paf=P*100, paf_lo=Plo*100, paf_hi=Phi*100,
                tot=A/P, tot_lo=Alo/Phi, tot_hi=Ahi/Plo)

rows = []
for loc in LOCS:
    for y in [1990,1995,2000,2005,2010,2015,2018,2023]:
        d = agg(loc, y)
        if d: rows.append({"location": loc, "year": y, **d})
ui = pd.DataFrame(rows)
ui.to_csv(r"D:\work\_cra_ui.csv", index=False, encoding="utf-8-sig")

print("===== 2023（年龄标化 DALY，含 95% UI）=====")
v = ui[ui.year==2023].set_index("location").reindex(LOCS)
show = pd.DataFrame({
  "可归因率": v.attr.round(1).astype(str) + " (" + v.attr_lo.round(1).astype(str) + "–" + v.attr_hi.round(1).astype(str) + ")",
  "PAF%":     v.paf.round(1).astype(str) + " (" + v.paf_lo.round(1).astype(str) + "–" + v.paf_hi.round(1).astype(str) + ")",
  "推导总负担率": v.tot.round(1).astype(str) + " (" + v.tot_lo.round(1).astype(str) + "–" + v.tot_hi.round(1).astype(str) + ")",
})
print(show.to_string())
print("\nSAVED _cra_ui.csv")
