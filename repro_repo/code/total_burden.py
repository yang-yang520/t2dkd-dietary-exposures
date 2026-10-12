# -*- coding: utf-8 -*-
"""官方 T2DKD 总负担（病因级，无风险）主表 + 与反推值核验。
输入: IHME-GBD_2023_DATA-10edd7c8-1.csv (13 locations: 5 SDI + 7 region + Global)"""
import pandas as pd

f = r"D:\work\IHME-GBD_2023_DATA-10edd7c8-1.csv"
d = pd.read_csv(r"D:\work\IHME-GBD_2023_DATA-10edd7c8-1.csv")
d["measure"] = d.measure_name.map(lambda x: "DALY" if "DALY" in x else "Deaths")
d["metric"] = d.metric_name.map({"Number":"num","Rate":"rate","Percent":"pct"})
d["age"] = d.age_name.map(lambda x: "AS" if "standardized" in x else "AllAges")
d["stratum"] = d.location_name.map(lambda l: "SDI" if "SDI" in l else ("region" if l!="Global" else "global"))
t = d[["stratum","location_name","measure","age","metric","year","val","lower","upper"]].rename(columns={"location_name":"location"})
t = t.sort_values(["stratum","location","measure","age","metric","year"])
t.to_csv(r"D:\work\_total_burden.csv", index=False, encoding="utf-8-sig")
print("rows:", len(t), "| stratum:", t.stratum.value_counts().to_dict())

# ---- 核验：官方 vs 反推（年龄标化 DALY 率）----
OFF = t[(t.age=="AS")&(t.metric=="rate")&(t.measure=="DALY")].set_index(["location","year"])["val"]
DER = pd.read_csv(r"D:\work\_cra_ui.csv").set_index(["location","year"])["tot"]
c = pd.DataFrame({"official":OFF, "derived":DER}).dropna()
c["diff"] = c.official - c.derived
print(f"\n官方 vs 反推：n={len(c)}  max|diff|={c['diff'].abs().max():.2f}  mean|diff|={c['diff'].abs().mean():.3f}  r={c.official.corr(c.derived):.5f}")
print("\n官方总负担率（年龄标化 DALY）:")
SDI5=["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
REG7=["Sub-Saharan Africa","North Africa and Middle East","South Asia",
      "Southeast Asia, East Asia, and Oceania",
      "Central Europe, Eastern Europe, and Central Asia","Latin America and Caribbean","High-income"]
for y in [1990,2023]:
    print(f"  --{y}--")
    for loc in SDI5+["Global"]+REG7:
        if (loc,y) in OFF.index: print(f"    {loc:48s} {OFF.loc[(loc,y)]:7.1f}")
print("\nSAVED _total_burden.csv")
