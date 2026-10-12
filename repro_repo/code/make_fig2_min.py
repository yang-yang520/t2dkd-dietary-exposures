# -*- coding: utf-8 -*-
"""Fig 2：分两图生成 SHAP 蜂群（单图模式，避免子图干扰），再用 PIL 拼接。"""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from sklearn.ensemble import RandomForestRegressor
from PIL import Image, ImageDraw, ImageFont
import os

FE = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g","whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
LB = {"sodium_mg":"Dietary sodium (mg/d)","ssb_g":"Sugar-sweetened beverages (g/d)",
      "unproc_red_meat_g":"Unprocessed red meat (g/d)","proc_meat_g":"Total processed meats (g/d)",
      "whole_grains_g":"Whole grains (g/d)","refined_grains_g":"Refined grains (g/d)",
      "beans_legumes_g":"Beans & legumes (g/d)","fruits_g":"Fruits (g/d)"}
FL = [LB[f] for f in FE]
p2 = pd.read_csv(r"D:\work\_panel.csv").dropna(subset=FE+["ASIR","DALY_rate"])
X = p2[FE].values

outs = []
for col, title, tag in [("ASIR","a  Incidence (ASIR)","A"), ("DALY_rate","b  Disability (DALY rate)","B")]:
    rf = RandomForestRegressor(n_estimators=500, max_features=2, random_state=123, n_jobs=-1).fit(X, p2[col].values)
    sv = np.asarray(shap.TreeExplainer(rf).shap_values(X))
    if sv.ndim == 3: sv = sv[:, :, 0]
    fig = plt.figure(figsize=(8, 6), dpi=300)
    expl = shap.Explanation(values=sv, base_values=float(np.mean(rf.predict(X))), data=X, feature_names=FL)
    shap.plots.beeswarm(expl, show=False, max_display=8, color_bar=True)
    plt.title(title, fontsize=12)
    p = rf"D:\work\_fig2_panel_{tag}.png"
    fig.savefig(p, bbox_inches="tight", dpi=300); plt.close(fig); outs.append(p)
    print("panel", tag, "saved")

# ---- 拼接 ----
def font(sz):
    for f in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"]:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, sz)
            except Exception: pass
    return ImageFont.load_default()

a = Image.open(outs[0]).convert("RGB"); b = Image.open(outs[1]).convert("RGB")
W = 1700
a = a.resize((W, int(a.height*W/a.width)), Image.LANCZOS)
b = b.resize((W, int(b.height*W/b.width)), Image.LANCZOS)
TITLE_H, PAD = 8, 30
c = Image.new("RGB", (W*2+PAD, TITLE_H+max(a.height,b.height)+PAD), "white")
c.paste(a, (0, TITLE_H)); c.paste(b, (W+PAD, TITLE_H))
c.save(r"D:\work\Fig2_importance.png", dpi=(300,300))
c.save(r"D:\work\Fig2_importance.tiff", dpi=(300,300), compression="tiff_lzw")
print("SAVED Fig2_importance.png/.tiff", c.size)
