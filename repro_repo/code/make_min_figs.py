# -*- coding: utf-8 -*-
"""精简版 4 图（从数据重绘，图号/标注统一）。
  Fig1: (A) 8 膳食区域趋势 + (B) T2DKD 负担区域趋势
  Fig2: (A) 发病率 SHAP  (B) DALY SHAP（回归模型）
  Fig3: (A) 钠-SDI  (B) SSB-SDI  (C) 豆类-SDI  (D) DALY率-SDI (LOWESS)
  Fig4: (A) 可归因率 by SDI  (B) by super-region  (C) PAF by SDI（堆叠）
"""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy import stats

plt.rcParams.update({"font.size":9,"axes.titlesize":10,"axes.labelsize":9,
                     "xtick.labelsize":8.5,"ytick.labelsize":8.5,"legend.fontsize":8,
                     "axes.spines.top":False,"axes.spines.right":False})
SAVE = dict(dpi=300, bbox_inches="tight")

# ---------------- 数据 ----------------
panel = pd.read_csv(r"D:\work\_panel.csv")
name_iso3 = dict(zip(panel.iso3, panel.location_name))   # iso3 -> 地名
s = pd.read_excel(r"D:\work\DS-GDD-analysis Dietary sodium.xlsx", header=1)
s.columns = ["国家","年份","区域","SDI","数值"]
region_map = dict(zip(s.国家, s.区域))
REGION_ORDER = ["High-Income Countries","Central/Eastern Europe and Central Asia",
                "Latin America/Caribbean","Middle East/North Africa","South Asia",
                "Southeast and East Asia","Sub-Saharan Africa"]
RCOL = plt.cm.tab10(np.linspace(0,1,len(REGION_ORDER)))

diet = pd.read_csv(r"D:\work\_diet_national.csv")
diet["region"] = diet["iso3"].map(name_iso3).map(region_map); diet = diet.dropna(subset=["region"])

gbd = pd.read_csv(r"D:\work\IHME-GBD_2023_DATA-582b4132-1.csv")
inc = gbd[gbd.measure_name=="Incidence"][["location_name","year","val"]].rename(columns={"val":"ASIR"})
daly = gbd[gbd.measure_name.str.contains("DALY")][["location_name","year","val"]].rename(columns={"val":"DALY_rate"})
burden = inc.merge(daly, on=["location_name","year"])
burden["region"] = burden["location_name"].map(region_map); burden = burden.dropna(subset=["region"])

# ================= Figure 1 =================
FACTORS = [("sodium_mg","Dietary sodium (mg/d)"),("ssb_g","SSB (g/d)"),
           ("refined_grains_g","Refined grains (g/d)"),("beans_legumes_g","Beans & legumes (g/d)"),
           ("whole_grains_g","Whole grains (g/d)"),("fruits_g","Fruits (g/d)"),
           ("unproc_red_meat_g","Unprocessed red meat (g/d)"),("proc_meat_g","Processed meat (g/d)")]
fig = plt.figure(figsize=(16, 9.6), dpi=300)
gs = fig.add_gridspec(3, 4, hspace=0.55, wspace=0.32)
letters = "ABCDEFGHIJ"
for i, (feat, label) in enumerate(FACTORS):
    ax = fig.add_subplot(gs[i//4, i%4])
    grp = diet.groupby(["region","year"])[feat].mean().reset_index()
    for j, reg in enumerate(REGION_ORDER):
        dgr = grp[grp.region==reg]
        if len(dgr): ax.plot(dgr.year, dgr[feat], color=RCOL[j], lw=1.3, label=reg)
    g = diet.groupby("year")[feat].mean()
    ax.plot(g.index, g.values, color="black", lw=2.0, ls="--", label="Global mean")
    ax.set_title(f"{letters[i].lower()} {label}", loc="left", fontsize=9.5)
    ax.set_xlabel("Year"); ax.grid(alpha=0.25, lw=0.4)
for k, (col, lab) in enumerate([("ASIR","ASIR (per 100,000)"),("DALY_rate","DALY rate (per 100,000)")]):
    ax = fig.add_subplot(gs[2, k*2:(k+1)*2])
    grp = burden.groupby(["region","year"])[col].mean().reset_index()
    for j, reg in enumerate(REGION_ORDER):
        dgr = grp[grp.region==reg]
        if len(dgr): ax.plot(dgr.year, dgr[col], color=RCOL[j], lw=1.4, label=reg)
    g = burden.groupby("year")[col].mean()
    ax.plot(g.index, g.values, color="black", lw=2.2, ls="--", label="Global mean")
    ax.set_title(f"{letters[8+k].lower()} {lab}", loc="left", fontsize=9.5)
    ax.set_xlabel("Year"); ax.grid(alpha=0.25, lw=0.4)
h, l = fig.axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.015), fontsize=8)
fig.suptitle("", fontsize=13, y=0.99)
fig.savefig(r"D:\work\Fig1_trends.png", **SAVE)
fig.savefig(r"D:\work\Fig1_trends.tiff", pil_kwargs={"compression":"tiff_lzw"}, **SAVE)
plt.close(fig); print("Fig1 done")

# ================= Figure 2（回归 SHAP） =================
import shap
from sklearn.ensemble import RandomForestRegressor
FE = ["sodium_mg","ssb_g","unproc_red_meat_g","proc_meat_g","whole_grains_g","refined_grains_g","beans_legumes_g","fruits_g"]
LB = {"sodium_mg":"Dietary sodium (mg/d)","ssb_g":"Sugar-sweetened beverages (g/d)",
      "unproc_red_meat_g":"Unprocessed red meat (g/d)","proc_meat_g":"Total processed meats (g/d)",
      "whole_grains_g":"Whole grains (g/d)","refined_grains_g":"Refined grains (g/d)",
      "beans_legumes_g":"Beans & legumes (g/d)","fruits_g":"Fruits (g/d)"}
FL = [LB[f] for f in FE]
p2 = pd.read_csv(r"D:\work\_panel.csv").dropna(subset=FE+["ASIR","DALY_rate"])
X = p2[FE].values
fig = plt.figure(figsize=(13.5, 5.4), dpi=300)
for k, (col, title) in enumerate([("ASIR","(A) Incidence (ASIR)"),("DALY_rate","(B) Disability (DALY rate)")]):
    ax = fig.add_subplot(1, 2, k+1)
    rf = RandomForestRegressor(n_estimators=500, max_features=2, random_state=123, n_jobs=-1).fit(X, p2[col].values)
    sv = np.asarray(shap.TreeExplainer(rf).shap_values(X))
    if sv.ndim == 3: sv = sv[:, :, 0]
    expl = shap.Explanation(values=sv, base_values=float(np.mean(rf.predict(X))), data=X, feature_names=FL)
    plt.sca(ax); shap.plots.beeswarm(expl, show=False, max_display=8, color_bar=True)
    ax.set_title(title, loc="left", fontsize=11)
fig.suptitle("", fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(r"D:\work\Fig2_importance.png", **SAVE)
fig.savefig(r"D:\work\Fig2_importance.tiff", pil_kwargs={"compression":"tiff_lzw"}, **SAVE)
plt.close(fig); print("Fig2 done")

# ================= Figure 3（SDI） =================
panel_sdi = pd.read_csv(r"D:\work\_panel_sdi.csv")
long_sdi = pd.read_csv(r"D:\work\_sdi_204_long.csv")
c204 = pd.read_csv(r"D:\work\GBD_T2DKD_SDI_204countries处理后_v2.csv")
sdi2018 = long_sdi[long_sdi.year==2018][["location_name","sdi"]].rename(columns={"sdi":"sdi_2018"})
f5 = c204.merge(sdi2018, on="location_name", how="left")
QORDER = ["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
QCOLOR = {"Low SDI":"#d7191c","Low-middle SDI":"#fdae61","Middle SDI":"#ffffbf",
          "High-middle SDI":"#abd9e9","High SDI":"#2c7bb6"}
C90, C18 = "#2c6fbb", "#d95f02"

def lowess(x, y, frac=0.5, it=3):
    n=len(x); x=np.asarray(x,float); y=np.asarray(y,float)
    o=np.argsort(x); xs=x[o]; ys=y[o]; k=max(2,int(np.ceil(frac*n)))
    h=np.array([np.sort(np.abs(xs-xs[i]))[k-1] for i in range(n)]); h=np.clip(h,1e-12,None)
    d=np.abs(xs[:,None]-xs[None,:])/h[None,:]; W=np.where(d<1.0,(1.0-d**3)**3,0.0)
    rw=np.ones(n); ye=ys.copy()
    for _ in range(it):
        for i in range(n):
            wi=W[:,i]*rw
            if wi.sum()==0: ye[i]=ys[i]; continue
            A=np.vstack([xs,np.ones(n)]).T
            b=np.linalg.lstsq(A*np.sqrt(wi)[:,None],ys*np.sqrt(wi),rcond=None)[0]; ye[i]=xs[i]*b[0]+b[1]
        res=ys-ye; sw=np.median(np.abs(res))
        if sw<1e-12: break
        rw=np.where(np.abs(res)>6*sw,0.0,(1.0-(res/(6*sw))**2)**2)
    return xs,ye

fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.0), dpi=300)
for ax,(label,feat,letter) in zip(axes.flat[:3], [
        ("Dietary sodium (mg/d)","sodium_mg","A"),
        ("Sugar-sweetened beverages (g/d)","ssb_g","B"),
        ("Beans & legumes (g/d)","beans_legumes_g","C")]):
    lines=[]
    for year,color,marker,ls in [(1990,C90,"o","--"),(2018,C18,"^","-")]:
        d = panel_sdi[panel_sdi.year==year][["sdi_year",feat]].dropna()
        x=d["sdi_year"].astype(float); y=d[feat].astype(float)
        ax.scatter(x,y,color=color,marker=marker,s=22,alpha=0.6,edgecolor="white",linewidth=0.3,zorder=3)
        sl,ic,r,p,_=stats.linregress(x,y); xs=np.linspace(x.min(),x.max(),50)
        ax.plot(xs,ic+sl*xs,color=color,lw=1.6,ls=ls,zorder=2)
        lines.append(f"{year}: R={r:.2f}, p={'<0.001' if p<0.001 else round(p,3)}")
    ax.text(0.03,0.97,"\n".join(lines),transform=ax.transAxes,va="top",fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3",fc="white",ec="0.8",alpha=0.85))
    ax.set_xlabel("SDI"); ax.set_ylabel(label)
    ax.set_title(f"{letter.lower()} {label}", loc="left", fontsize=10.5); ax.grid(alpha=0.25,lw=0.5)
ax = axes.flat[3]
d = f5.dropna(subset=["sdi_2018","DALY_rate"])
for q in QORDER:
    m=d[d.quintile_2023==q]
    ax.scatter(m["sdi_2018"],m["DALY_rate"],s=22,color=QCOLOR[q],alpha=0.75,edgecolor="white",linewidth=0.3,zorder=3,label=q)
xs,ys = lowess(d["sdi_2018"].values.astype(float), d["DALY_rate"].values.astype(float), frac=0.6)
ax.plot(xs,ys,color="0.15",lw=2.2,zorder=4,label="LOWESS")
pk=float(xs[np.argmax(ys)]); ax.axvline(pk,color="0.5",ls=":",lw=1.2,zorder=2)
ax.text(pk, ax.get_ylim()[1]*0.95, f" peak SDI≈{pk:.2f}", fontsize=8.5, color="0.3")
ax.set_xlabel("SDI (2018)"); ax.set_ylabel("DALY rate (per 100,000)")
ax.set_title("(D) T2DKD DALY rate vs SDI (2018, LOWESS)", loc="left", fontsize=10.5); ax.grid(alpha=0.25,lw=0.5)
h=[plt.Line2D([],[],marker="o",ls="--",color=C90,label="1990"),plt.Line2D([],[],marker="^",ls="-",color=C18,label="2018"),
   plt.Line2D([],[],ls=":",color="0.5",label="peak SDI")]
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5,-0.02))
fig.suptitle("", fontsize=13, y=1.0)
fig.tight_layout(rect=[0,0.02,1,0.98])
fig.savefig(r"D:\work\Fig3_SDI.png", **SAVE)
fig.savefig(r"D:\work\Fig3_SDI.tiff", pil_kwargs={"compression":"tiff_lzw"}, **SAVE)
plt.close(fig); print("Fig3 done")

# ================= Figure 4（归因） =================
m = pd.read_csv(r"D:\work\_cra_master_long.csv"); AS = m[m.age=="AS"]
SDI_O=["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
SHORT={"Low SDI":"Low","Low-middle SDI":"Low-mid","Middle SDI":"Middle","High-middle SDI":"High-mid","High SDI":"High"}
REG_O=["Sub-Saharan Africa","North Africa and Middle East","South Asia","Southeast Asia, East Asia, and Oceania",
       "Central Europe, Eastern Europe, and Central Asia","Latin America and Caribbean","High-income"]
REG_S={"Sub-Saharan Africa":"Sub-Saharan Africa","North Africa and Middle East":"N. Africa & Mid. East","South Asia":"South Asia",
       "Southeast Asia, East Asia, and Oceania":"SE/E. Asia & Oceania",
       "Central Europe, Eastern Europe, and Central Asia":"C./E. Europe & C. Asia",
       "Latin America and Caribbean":"Latin America & Carib.","High-income":"High-income"}
SDI_RAMP=["#86b6ef","#5598e7","#2a78d6","#1c5cab","#104281"]
RISK_O=["Fruits (low)","Whole grains (low)","Red meat (high)","Processed meat (high)","SSB (high)","Sodium (high)"]
RISK_C=dict(zip(RISK_O,["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300"]))
INK,SEC,MUTED,GRID,BASE="#0b0b0b","#52514e","#898781","#e1e0d9","#c3c2b7"
YEARS=[1990,1995,2000,2005,2010,2015,2018,2023]

def tot(loc_pool, measure, order):
    out={}
    for loc in order:
        s_=AS[(AS.measure==measure)&(AS.location==loc)&(AS.metric=="rate")]
        out[loc]=s_.groupby("year")["val"].sum().reindex(YEARS)
    return out

fig, axes = plt.subplots(1, 3, figsize=(17.5, 5.0), dpi=300)
for ax, order, cols, smap, tag, ttl in [
        (axes[0], SDI_O, SDI_RAMP, SHORT, "A", "Attributable DALY rate by SDI quintile"),
        (axes[1], REG_O, ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7"], REG_S, "B", "Attributable DALY rate by super-region")]:
    T = tot(None,"DALY",order); g=AS[(AS.measure=="DALY")&(AS.location=="Global")&(AS.metric=="rate")].groupby("year")["val"].sum().reindex(YEARS)
    ends=[]
    for loc,c in zip(order,cols):
        ax.plot(YEARS,T[loc].values,color=c,lw=2,marker="o",ms=4,zorder=3)
        ends.append((smap[loc],T[loc].values[-1]))
    ax.plot(YEARS,g.values,color=MUTED,lw=1.6,ls=(0,(5,3)),zorder=2); ends.append(("Global",g.values[-1]))
    ax.margins(y=0.16); y0,y1=ax.get_ylim(); gap=(y1-y0)*0.058
    ends=sorted(ends,key=lambda t:t[1]); adj=[e[1] for e in ends]
    for i in range(1,len(adj)):
        if adj[i]-adj[i-1]<gap: adj[i]=adj[i-1]+gap
    if adj[-1]>y1:
        sh=adj[-1]-y1; adj=[a-sh for a in adj]
    for (lab,y),ya in zip(ends,adj):
        ax.annotate(lab,xy=(2023,y),xytext=(2024.6,ya),va="center",ha="left",fontsize=8,color=SEC,
                    annotation_clip=False,arrowprops=dict(arrowstyle="-",color=BASE,lw=0.7,shrinkA=0,shrinkB=2))
    ax.set_title(f"{tag.lower()}  {ttl}", loc="left", fontsize=11, color=INK, fontweight="bold", pad=8)
    ax.set_ylabel("DALYs per 100,000"); ax.set_xlabel("Year"); ax.set_xlim(1988,2032)
    ax.set_xticks(YEARS); ax.tick_params(axis="x",rotation=45); ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.grid(axis="y",color=GRID,lw=0.8,zorder=0)
ax = axes[2]
d23 = AS[(AS.measure=="DALY")&(AS.year==2023)&(AS.metric=="paf")&(AS.location.isin(SDI_O))]
piv = d23.pivot_table(index="location",columns="risk",values="val").reindex(SDI_O)[RISK_O]*100
xs=np.arange(len(piv)); bottom=np.zeros(len(piv))
for r in RISK_O:
    v=piv[r].values
    ax.bar(xs,v,bottom=bottom,color=RISK_C[r],width=0.72,edgecolor="white",linewidth=1.4,zorder=3)
    for xx,vv,bb in zip(xs,v,bottom):
        if vv>=2.2: ax.text(xx,bb+vv/2,f"{vv:.1f}",ha="center",va="center",fontsize=7.4,color="white",zorder=4)
    bottom+=v
for xx,tt_ in zip(xs,bottom): ax.text(xx,tt_+0.5,f"{tt_:.0f}",ha="center",va="bottom",fontsize=8.5,fontweight="bold")
ax.set_xticks(xs); ax.set_xticklabels([SHORT[q] for q in piv.index],fontsize=8.5)
ax.set_ylim(0,40); ax.set_ylabel("PAF (%), attributable fraction"); ax.grid(axis="y",color=GRID,lw=0.8,zorder=0)
ax.set_title("(C)  Attributable fraction (PAF) by SDI, 2023", loc="left", fontsize=11, color=INK, fontweight="bold", pad=8)
ax.legend(handles=[plt.Line2D([],[],color=RISK_C[r],lw=7) for r in RISK_O], labels=RISK_O,
          fontsize=7.4, frameon=False, loc="center left", bbox_to_anchor=(1.02,0.5))
fig.suptitle("", fontsize=12.5, fontweight="bold", x=0.006, ha="left", y=1.02)
fig.tight_layout(rect=[0,0,0.99,0.98])
fig.savefig(r"D:\work\Fig4_attributable.png", **SAVE)
fig.savefig(r"D:\work\Fig4_attributable.tiff", pil_kwargs={"compression":"tiff_lzw"}, **SAVE)
plt.close(fig); print("Fig4 done")
print("ALL DONE")
