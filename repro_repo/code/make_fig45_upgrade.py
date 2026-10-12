# -*- coding: utf-8 -*-
"""① Fig4 增 (D) 单风险 PAF + 95%UI   ②③ 新增 Fig5「分解框架」4 面板。
"""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

INK,SEC,MUTED,GRID,BASE = "#0b0b0b","#52514e","#898781","#e1e0d9","#c3c2b7"
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
YEARS=[1990,1995,2000,2005,2010,2015,2018,2023]

m = pd.read_csv(r"D:\work\_cra_master_long.csv"); AS=m[m.age=="AS"]
ui = pd.read_csv(r"D:\work\_cra_ui.csv")

def style(ax, ygrid=True):
    ax.set_facecolor("#fcfcfb")
    if ygrid: ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color(BASE)
    ax.tick_params(colors=MUTED, labelsize=8.3)

# ================= Fig 4（A,B,C 同前 + D 单风险 UI）=================
def tot_series(loc, measure="DALY"):
    s=AS[(AS.location==loc)&(AS.measure==measure)&(AS.metric=="rate")]
    return s.groupby("year")["val"].sum().reindex(YEARS)

fig, axes = plt.subplots(1, 4, figsize=(21.5, 5.0), dpi=300, gridspec_kw={"width_ratios":[1.0,1.15,0.95,1.15]})
for ax, order, cols, smap, tag, ttl in [
        (axes[0], SDI_O, SDI_RAMP, SHORT, "A", "Attributable DALY rate by SDI"),
        (axes[1], REG_O, ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7"], REG_S, "B", "by super-region")]:
    g = tot_series("Global")
    ends=[]
    for loc,c in zip(order,cols):
        y=tot_series(loc); ax.plot(YEARS,y.values,color=c,lw=2,marker="o",ms=4,zorder=3); ends.append((smap[loc],y.values[-1]))
    ax.plot(YEARS,g.values,color=MUTED,lw=1.6,ls=(0,(5,3)),zorder=2); ends.append(("Global",g.values[-1]))
    ax.margins(y=0.16); y0,y1=ax.get_ylim(); gap=(y1-y0)*0.058
    ends=sorted(ends,key=lambda t:t[1]); adj=[e[1] for e in ends]
    for i in range(1,len(adj)):
        if adj[i]-adj[i-1]<gap: adj[i]=adj[i-1]+gap
    if adj[-1]>y1: sh=adj[-1]-y1; adj=[a-sh for a in adj]
    for (lab,y),ya in zip(ends,adj):
        ax.annotate(lab,xy=(2023,y),xytext=(2024.6,ya),va="center",ha="left",fontsize=8,color=SEC,
                    annotation_clip=False,arrowprops=dict(arrowstyle="-",color=BASE,lw=0.7,shrinkA=0,shrinkB=2))
    ax.set_title(f"{tag.lower()} {ttl}",loc="left",fontsize=10.5,color=INK,fontweight="bold",pad=8)
    ax.set_ylabel("DALYs per 100,000"); ax.set_xlabel("Year"); ax.set_xlim(1988,2032); ax.set_xticks(YEARS)
    ax.tick_params(axis="x",rotation=45); ax.yaxis.set_major_locator(MaxNLocator(5)); style(ax)

ax=axes[2]
d23=AS[(AS.measure=="DALY")&(AS.year==2023)&(AS.metric=="paf")&(AS.location.isin(SDI_O))]
piv=d23.pivot_table(index="location",columns="risk",values="val").reindex(SDI_O)[RISK_O]*100
xs=np.arange(len(piv)); bottom=np.zeros(len(piv))
for r in RISK_O:
    v=piv[r].values
    ax.bar(xs,v,bottom=bottom,color=RISK_C[r],width=0.72,edgecolor="white",linewidth=1.4,zorder=3)
    for xx,vv,bb in zip(xs,v,bottom):
        if vv>=2.2: ax.text(xx,bb+vv/2,f"{vv:.1f}",ha="center",va="center",fontsize=7.2,color="white",zorder=4)
    bottom+=v
for xx,t_ in zip(xs,bottom): ax.text(xx,t_+0.5,f"{t_:.0f}",ha="center",va="bottom",fontsize=8.5,fontweight="bold")
ax.set_xticks(xs); ax.set_xticklabels([SHORT[q] for q in piv.index],fontsize=8.5)
ax.set_ylim(0,40); ax.set_ylabel("PAF (%)"); ax.set_title("(C) PAF by SDI, 2023",loc="left",fontsize=10.5,color=INK,fontweight="bold",pad=8)
ax.legend(handles=[plt.Line2D([],[],color=RISK_C[r],lw=7) for r in RISK_O],labels=RISK_O,
          fontsize=7.0,frameon=False,loc="center left",bbox_to_anchor=(1.01,0.5)); style(ax)

ax=axes[3]
P=AS[(AS.measure=="DALY")&(AS.year==2023)&(AS.metric=="paf")]
pv=P.pivot_table(index="risk",columns="location",values="val")*100
lv=P.pivot_table(index="risk",columns="location",values="lower")*100
uv=P.pivot_table(index="risk",columns="location",values="upper")*100
offs=np.linspace(0.32,-0.32,len(SDI_O))
for i,r in enumerate(RISK_O):
    for j,q in enumerate(SDI_O):
        yy=i+offs[j]; x=pv.loc[r,q]
        ax.plot([lv.loc[r,q],uv.loc[r,q]],[yy,yy],color=SDI_RAMP[j],lw=2.4,solid_capstyle="round",alpha=0.9,zorder=3)
        ax.plot([x],[yy],marker="o",ms=5,color=SDI_RAMP[j],zorder=4)
ax.set_yticks(range(len(RISK_O))); ax.set_yticklabels(RISK_O,fontsize=8.3)
ax.invert_yaxis(); ax.set_xlabel("PAF (%), 95% UI, 2023"); ax.set_xlim(-1,20)
ax.set_title("(D) PAF by risk with 95% UI",loc="left",fontsize=10.5,color=INK,fontweight="bold",pad=8)
ax.legend(handles=[plt.Line2D([],[],color=SDI_RAMP[j],lw=6,label=SHORT[q]) for j,q in enumerate(SDI_O)],
          fontsize=7.4,frameon=False,loc="lower right"); style(ax, ygrid=False)
fig.suptitle("",
             x=0.005, ha="left", fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout(rect=[0,0,0.99,0.98])
fig.savefig(r"D:\work\Fig4_attributable.png", dpi=300, bbox_inches="tight")
fig.savefig(r"D:\work\Fig4_attributable.tiff", dpi=300, bbox_inches="tight", pil_kwargs={"compression":"tiff_lzw"})
plt.close(fig); print("Fig4 (A-D) done")

# ================= Fig 5：分解框架（横轴=官方总负担率）=================
TB = pd.read_csv(r"D:\work\_total_burden.csv")
TB = TB[(TB.age=="AS")&(TB.metric=="rate")&(TB.measure=="DALY")].set_index(["location","year"])["val"]
tot23 = TB.xs(2023, level="year")
paf23 = ui[ui.year==2023].set_index("location")["paf"]
v23 = pd.DataFrame({"tot": tot23, "paf": paf23})
fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.4), dpi=300)

# (A)(B) 象限
for ax, order, cmap, smap, tag in [(axes[0,0], SDI_O, SDI_RAMP, SHORT, "A"),
                                   (axes[0,1], REG_O, ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7"], REG_S, "B")]:
    gx, gy = v23.loc["Global","tot"], v23.loc["Global","paf"]
    xs_ = [v23.loc[l,"tot"] for l in order]; ys_ = [v23.loc[l,"paf"] for l in order]
    x0, x1 = 0, max(xs_)*1.28; y0, y1 = min(ys_)*0.90, max(ys_)*1.12
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    # 优先象限（高负担 + 高膳食占比）浅底色
    ax.fill_between([gx, x1], gy, y1, color="#f6dede", zorder=0)
    ax.axvline(gx, color=MUTED, ls=":", lw=1.2, zorder=1)
    ax.axhline(gy, color=MUTED, ls=":", lw=1.2, zorder=1)
    placed = []                      # 已占用的标签框（数据坐标）
    lw_ = (x1-x0)*0.13; lh_ = (y1-y0)*0.055
    cand = [(10,8,"left"), (10,-14,"left"), (-10,8,"right"), (-10,-14,"right"), (10,20,"left"), (-10,20,"right")]
    for i,loc in enumerate(order):
        x,y = v23.loc[loc,"tot"], v23.loc[loc,"paf"]
        ax.scatter([x],[y], s=95, color=cmap[i], edgecolor="white", linewidth=1.0, zorder=5)
        bx = x + (lw_ if True else 0)
        # 选择一个不重叠的偏移
        dx = dy = 0; ha = "left"
        for ox, oy, h in cand:
            lx = x + (ox/10)*(lw_/1.0) * (1 if h=="left" else -1)
            ly = y + (oy/10)*(lh_/1.0)*1.6
            box = (lx-lw_/2, ly-lh_/2, lx+lw_/2, ly+lh_/2) if h=="left" else (lx-lw_, ly-lh_/2, lx, ly+lh_/2)
            if not any(not(box[2]<b[0] or b[2]<box[0] or box[3]<b[1] or b[3]<box[1]) for b in placed):
                dx, dy, ha = ox, oy, h; placed.append(box); break
        else:
            placed.append((x, y, x+lw_, y+lh_))
        ax.annotate(smap[loc], xy=(x,y), xytext=(dx,dy), textcoords="offset points",
                    ha=ha, fontsize=8.4, color=SEC, zorder=6)
    ax.text(x1*0.995, y1*0.985, "High burden +\nhigh sum of PAFs", transform=ax.transData,
            ha="right", va="top", fontsize=8.4, color="#b03030", fontweight="bold", zorder=5)
    ax.text(x1*0.995, y0*1.01, "global values", ha="right", va="bottom", fontsize=7.2, color=MUTED, zorder=5)
    ax.set_xlabel("Total T2DKD DALY rate (per 100,000)")
    ax.set_ylabel("Attributable fraction, PAF (%)")
    ax.set_title(f"{tag.lower()}  Total burden vs sum of risk-specific PAFs, 2023", loc="left", fontsize=11, color=INK, fontweight="bold", pad=8)
    style(ax)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)

# (C)(D) 时间分解（按 SDI）
uu = ui[ui.location.isin(SDI_O)]
for ax, col, tag, ttl, ylab in [(axes[1,0], "tot", "C", "Total T2DKD DALY rate by SDI, 1990–2023", "DALYs per 100,000"),
                                (axes[1,1], "paf", "D", "Attributable fraction by SDI, 1990–2023", "PAF (%)")]:
    ends=[]
    for j,q in enumerate(SDI_O):
        s = (TB.loc[q].reindex(YEARS) if col=="tot" else uu[uu.location==q].set_index("year")[col].reindex(YEARS))
        ax.plot(YEARS,s.values,color=SDI_RAMP[j],lw=2,marker="o",ms=4,zorder=3); ends.append((SHORT[q],s.values[-1]))
    if col=="paf":
        g=ui[ui.location=="Global"].set_index("year")[col].reindex(YEARS)
        ax.plot(YEARS,g.values,color=MUTED,lw=1.6,ls=(0,(5,3)),zorder=2); ends.append(("Global",g.values[-1]))
    ax.margins(y=0.16); y0,y1=ax.get_ylim(); gap=(y1-y0)*0.058
    ends=sorted(ends,key=lambda t:t[1]); adj=[e[1] for e in ends]
    for i in range(1,len(adj)):
        if adj[i]-adj[i-1]<gap: adj[i]=adj[i-1]+gap
    if adj[-1]>y1: sh=adj[-1]-y1; adj=[a-sh for a in adj]
    for (lab,y),ya in zip(ends,adj):
        ax.annotate(lab,xy=(2023,y),xytext=(2024.6,ya),va="center",ha="left",fontsize=8,color=SEC,
                    annotation_clip=False,arrowprops=dict(arrowstyle="-",color=BASE,lw=0.7,shrinkA=0,shrinkB=2))
    ax.set_title(f"{tag.lower()}  {ttl}", loc="left", fontsize=11, color=INK, fontweight="bold", pad=8)
    ax.set_ylabel(ylab); ax.set_xlabel("Year"); ax.set_xlim(1988,2032); ax.set_xticks(YEARS)
    ax.tick_params(axis="x",rotation=45); ax.yaxis.set_major_locator(MaxNLocator(5)); style(ax)

fig.suptitle("",
             x=0.006, ha="left", fontsize=12.5, fontweight="bold", y=1.0)
fig.text(0.006,-0.02,"Attributable rate = total burden rate × sum of six risk-specific dietary PAFs. "
         "a,b Each point is one SDI quintile or super-region in 2023; "
         "dotted lines mark the global values, dividing the plane into four descriptive quadrants. c,d Trajectories of the two "
         "components (total T2DKD DALY rate and the sum of risk-specific PAFs) by SDI quintile, 1990–2023. Total burden rate is the GBD 2023 "
         "age-standardized estimate (both sexes).",
         ha="left", fontsize=8.0, color=MUTED)
fig.tight_layout(rect=[0,0.01,1,0.98])
fig.savefig(r"D:\work\Fig5_decomposition.png", dpi=300, bbox_inches="tight")
fig.savefig(r"D:\work\Fig5_decomposition.tiff", dpi=300, bbox_inches="tight", pil_kwargs={"compression":"tiff_lzw"})
plt.close(fig); print("Fig5 done")

# Table 4 数据：PAF by risk x SDI with UI
rows=[]
for r in RISK_O:
    row={}
    for q in SDI_O+["Global"]:
        row[SHORT.get(q,"Global")] = f"{pv.loc[r,q]:.1f} ({lv.loc[r,q]:.1f}–{uv.loc[r,q]:.1f})"
    rows.append({"Dietary risk": r, **row})
pd.DataFrame(rows).to_csv(r"D:\work\Table4_PAF_by_risk_SDI.csv", index=False, encoding="utf-8-sig")
print("SAVED Table4_PAF_by_risk_SDI.csv")
print("DONE")
