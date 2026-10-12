# -*- coding: utf-8 -*-
"""第9条配套：Figure 5 象限敏感性——13 个地点在两种切点下的分类。"""
import pandas as pd

ROOT = r"D:\work"
ui = pd.read_csv(f"{ROOT}\\_cra_ui.csv")
tb = pd.read_csv(f"{ROOT}\\_total_burden.csv")
tb = tb[(tb.age=="AS")&(tb.metric=="rate")&(tb.measure=="DALY")].set_index(["location","year"])["val"]

SDI5 = ["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
REG7 = ["Sub-Saharan Africa","North Africa and Middle East","South Asia",
        "Southeast Asia, East Asia, and Oceania",
        "Central Europe, Eastern Europe, and Central Asia","Latin America and Caribbean","High-income"]
locs = SDI5 + ["Global"] + REG7

# 2023 的 total burden rate 与 summed PAF
rows = []
for loc in locs:
    t23 = tb.loc[(loc, 2023)]
    p23 = ui[(ui.location==loc)&(ui.year==2023)].iloc[0]["paf"]
    rows.append({"location": loc, "total_burden_rate": t23, "summed_PAF": p23})
df = pd.DataFrame(rows)

# 切点1：全球值；切点2：13 个地点（含 Global）的中位数
cut1_x, cut1_y = df[df.location=="Global"].iloc[0]["total_burden_rate"], df[df.location=="Global"].iloc[0]["summed_PAF"]
cut2_x, cut2_y = df["total_burden_rate"].median(), df["summed_PAF"].median()

def classify(x, y, cx, cy):
    hi_x = x > cx; hi_y = y > cy
    if hi_x and hi_y: return "高负担+高份额"
    if hi_x and not hi_y: return "高负担+低份额"
    if not hi_x and hi_y: return "低负担+高份额"
    return "低负担+低份额"

out = []
for _, r in df.iterrows():
    out.append([r.location, f"{r.total_burden_rate:.1f}", f"{r.summed_PAF:.1f}",
                classify(r.total_burden_rate, r.summed_PAF, cut1_x, cut1_y),
                classify(r.total_burden_rate, r.summed_PAF, cut2_x, cut2_y)])
res = pd.DataFrame(out, columns=["Location","Total burden rate (per 100,000)","Summed risk-specific PAF (%)",
                                 f"Quadrant (global cut: {cut1_x:.1f}/{cut1_y:.1f})",
                                 f"Quadrant (median cut: {cut2_x:.1f}/{cut2_y:.1f})"])
res.to_csv(f"{ROOT}\\_quadrant_classification.csv", index=False, encoding="utf-8-sig")
print("切点1 全球值:", round(cut1_x,1), round(cut1_y,1), "| 切点2 中位数:", round(cut2_x,1), round(cut2_y,1))
print(res.to_string(index=False))
