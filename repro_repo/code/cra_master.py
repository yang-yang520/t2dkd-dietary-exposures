# -*- coding: utf-8 -*-
"""统一数据源：只用「全合一」文件（0ed64a48）建 master 长表（Number/Rate/Percent 同源）。
   并核对它能否复现之前的 Table4（率）与 Table5（PAF）。"""
import pandas as pd, numpy as np

SRC = r"D:\work\IHME-GBD_2023_DATA-0ed64a48-1.csv"
SHORT = {"Diet low in fruits": "Fruits (low)", "Diet low in whole grains": "Whole grains (low)",
         "Diet high in red meat": "Red meat (high)", "Diet high in processed meat": "Processed meat (high)",
         "Diet high in sugar-sweetened beverages": "SSB (high)", "Diet high in sodium": "Sodium (high)"}
SDI = ["Low SDI", "Low-middle SDI", "Middle SDI", "High-middle SDI", "High SDI"]
REG = ["Central Europe, Eastern Europe, and Central Asia", "High-income", "Latin America and Caribbean",
       "North Africa and Middle East", "South Asia", "Southeast Asia, East Asia, and Oceania", "Sub-Saharan Africa"]
STRAT = {**{l: "SDI" for l in SDI + ["Global"]}, **{l: "region" for l in REG}}

d = pd.read_csv(SRC)
d["risk"] = d.rei_name.map(SHORT)
d["measure"] = d.measure_name.map(lambda x: "DALY" if "DALY" in x else "Deaths")
d["stratum"] = d.location_name.map(STRAT)
d["age"] = d.age_name.map(lambda x: "AS" if "standardized" in x else "AllAges")
d["metric"] = d.metric_name.map({"Number": "num", "Rate": "rate", "Percent": "paf"})
master = d[["stratum", "location_name", "risk", "measure", "age", "metric", "year", "val", "lower", "upper"]]
master = master.rename(columns={"location_name": "location"}).sort_values(
    ["stratum", "location", "measure", "risk", "age", "metric", "year"])
master.to_csv(r"D:\work\_cra_master_long.csv", index=False, encoding="utf-8-sig")
print("master rows:", len(master),
      "| stratum:", master.stratum.value_counts().to_dict(),
      "| metrics:", master.metric.unique().tolist())

AS = master[(master.age == "AS") & (master.metric == "rate")]
PAF = master[(master.age == "AS") & (master.metric == "paf")]

# --- 核对 Table4（6-risk 合计率）---
print("\n[核对 Table4] 6-risk 合计可归因率（AS, DALY）:")
for stratum in ["SDI", "region"]:
    s = AS[(AS.stratum == stratum) & (AS.measure == "DALY")]
    p = s.groupby(["location", "year"])["val"].sum().unstack()
    for loc in (["Global"] + (SDI if stratum == "SDI" else REG)):
        if loc in p.index:
            print(f"   {stratum:6s} {loc:48s} 1990={p.loc[loc,1990]:6.2f}  2023={p.loc[loc,2023]:6.2f}  "
                  f"d%={(p.loc[loc,2023]/p.loc[loc,1990]-1)*100:+5.1f}")

# --- 核对 Table5（PAF 合计）---
print("\n[核对 Table5] 2023 PAF 合计（AS, DALY, %）:")
q = PAF[(PAF.measure == "DALY") & (PAF.year == 2023)].groupby("location")["val"].sum() * 100
for loc in SDI + ["Global"] + REG:
    if loc in q.index: print(f"   {loc:48s} {q[loc]:5.1f}")
