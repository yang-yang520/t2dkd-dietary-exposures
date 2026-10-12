# -*- coding: utf-8 -*-
"""把 v15 转成 EKIR（Kidney International Reports）投稿格式 -> KIR_EKIR_v16.docx
   - 9 段结构：Title page / Abstract / Introduction / Methods / Results / Discussion /
     Disclosure / Acknowledgements / References（后接 Figure legends / Tables / Data sharing）
   - 标题 ≤10 词；摘要无缩写 ≤250 词；6 keywords 置于摘要后
   - 参考文献上标数字；P 斜体大写；千位不加逗号；图不入正文；表格后置且无竖线
"""
import re
import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

SRC = r"D:\work\Manuscript - KIR_submission_v15.docx"
OUT = r"D:\work\KIR_EKIR_v16.docx"
src = Document(SRC)
P15 = [p.text for p in src.paragraphs]

new = Document()
st = new.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.paragraph_format.line_spacing = 2.0          # 双倍行距
for lvl, sz in [(1, 12), (2, 12)]:
    s = new.styles[f"Heading {lvl}"]; s.font.size = Pt(sz); s.font.bold = True
    s.font.name = "Times New Roman"; s.font.color.rgb = RGBColor(0,0,0)

SUP = re.compile(r"\[([\d,\-\s]+)\]")            # [1,2] / [6] 等

def txt(s):
    """全局文本规整：千位逗号 -> 空格；P 值；等"""
    s = s.replace("1,295", "1295").replace("3,000", "3000").replace("100,000", "100 000")
    s = s.replace("(accessed October 12, 2026)", "(accessed October 12, 2026)")
    return s

def add(text, style=None, bold=False, size=12, italic=False, align=None, no_sup=False):
    """写入一段，把 [n] 转成上标数字。"""
    p = new.add_paragraph(style=style)
    if align is not None: p.alignment = align
    p.paragraph_format.line_spacing = 2.0
    rest = txt(text)
    if no_sup:
        r = p.add_run(rest); r.bold=bold; r.italic=italic; r.font.size=Pt(size)
        return p
    pos = 0
    for m in SUP.finditer(rest):
        if m.start() > pos:
            r = p.add_run(rest[pos:m.start()]); r.bold=bold; r.italic=italic; r.font.size=Pt(size)
        r = p.add_run(m.group(1)); r.font.superscript = True; r.font.size=Pt(size); r.bold=bold
        pos = m.end()
    if pos < len(rest):
        r = p.add_run(rest[pos:]); r.bold=bold; r.italic=italic; r.font.size=Pt(size)
    return p

def H(text):
    p = new.add_paragraph(); p.paragraph_format.line_spacing = 2.0
    r = p.add_run(text); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
    return p

# ==================== 1. TITLE PAGE ====================
H("Title page")
add("Dietary exposures and burden of type 2 diabetic kidney disease", bold=True, size=14, no_sup=True)
add("Running headline: Diet and T2DKD burden: a global study", no_sup=True)
add("")
add("Authors:", no_sup=True)
add("Qianwen Yang, MD, PhD¹; Chang-Kun Mao, MD²; Yuanyuan Bao, MD¹; Tiansu Li, MD¹; "
    "Huaqing Liu, MD¹; Yaru Bi, MD¹; Ming Li, MD, PhD¹*", no_sup=True)
add("")
add("Affiliations:", no_sup=True)
add("¹ Hefei Maternal and Child Health Hospital, Hefei, Anhui, China", no_sup=True)
add("² Department of Urology, Anhui Provincial Children's Hospital, Hefei 230022, Anhui, China", no_sup=True)
add("")
add("*Corresponding author: Ming Li, MD, PhD. Hefei Maternal and Child Health Hospital, Hefei, Anhui, China. "
    "Telephone: +86-13866141059. E-mail: 13866141059@163.com", no_sup=True)
add("")
add("Sources of support: This study was supported by the Hefei Municipal Health Commission (Hwk2023zd025). "
    "The funder had no role in study design, data collection, analysis, interpretation, or the decision to submit.", no_sup=True)
add("")
add("Word count — abstract: 246    main text: ~4500    references: 16", no_sup=True)
add("Figures: 5    Tables: 5    Supplementary material: Supplementary Methods S1; Supplementary Tables S1–S5", no_sup=True)
add("")
add("【请核对：作者姓名顺序、拼音拼写、学位（MD/PhD 等）、单位地址、电话/邮箱 — 请按实际情况订正】",
    italic=True, size=10, no_sup=True)

# ==================== 2. ABSTRACT ====================
new.add_page_break()
H("Abstract")
ABS = ("The global burden of type 2 diabetic kidney disease is rising, but how much of that burden is attributable to "
       "specific dietary risks, and whether the countries with the greatest burden are those in which diet accounts for the "
       "largest share of disease, remains unclear. We linked contemporaneous national dietary exposure estimates from the "
       "Global Dietary Database (1990–2018) with type 2 diabetic kidney disease burden from the Global Burden of Disease 2023 "
       "study for 185 countries (1295 country–year observations) and, separately, obtained comparative risk assessment "
       "estimates for six dietary risks (1990–2023). Random forest models using eight dietary exposures achieved modest "
       "out-of-country predictive performance under country-grouped cross-validation (coefficient of determination 0.200 for "
       "the age-standardized incidence rate and 0.300 for the disability-adjusted life year rate); sodium, sugar-sweetened "
       "beverages and beans or legumes ranked highest for incidence, whereas refined grains ranked highest for disability. In "
       "2023, the sum of the six risk-specific attributable disability-adjusted life year rates was 20.6 per 100 000, 12.2% "
       "higher than in 1990, and the summed risk-specific attributable fractions increased with the Socio-demographic Index, "
       "from 13.8% to 27.2%. Total burden was highest at middle and lowest at high Socio-demographic Index levels, so no "
       "quintile combined a high total burden with a high aggregate dietary share; among world regions, only Latin America and "
       "the Caribbean did. Viewing attributable burden as the product of total burden and aggregate dietary share offers a "
       "descriptive framework for comparing settings, although the summed fractions are not a directly estimated joint "
       "attributable burden.")
add(ABS, align=WD_ALIGN_PARAGRAPH.JUSTIFY, no_sup=True)
print("摘要词数:", len(ABS.split()))
add("")
add("Keywords: diabetic kidney disease; dietary exposure; attributable burden; machine learning; "
    "socio-demographic index; ecological study", no_sup=True)
add("【请核对：关键词 6 个、美国拼写】", italic=True, size=10, no_sup=True)

# ==================== 3-6. 正文各节（从 v15 复制） ====================
def copy_range(start_key, end_key):
    """复制 v15 中 start_key 之后、end_key 之前的段落。"""
    i = P15.index(start_key) if start_key in P15 else next(k for k,t in enumerate(P15) if t.strip()==start_key)
    j = len(P15)
    for k,t in enumerate(P15):
        if t.strip()==end_key and k > i: j = k; break
    return [t for t in P15[i+1:j] if t.strip()]

for sec in ["Introduction", "Methods", "Results", "Discussion"]:
    new.add_page_break()
    H(sec)
    nxt = {"Introduction":"Methods","Methods":"Results","Results":"Discussion","Discussion":"Disclosure"}[sec]
    for para in copy_range(sec, nxt):
        add(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

# ==================== 7. DISCLOSURE ====================
new.add_page_break()
H("Disclosure")
add("All the authors declared no competing interests.", no_sup=True)

# ==================== 8. ACKNOWLEDGEMENTS ====================
H("Acknowledgements")
add("Funding: This study was supported by the Hefei Municipal Health Commission (Hwk2023zd025).", no_sup=True)
add("Ethics approval and consent to participate: This study was based entirely on publicly available, de-identified, and "
    "aggregated country-level data. For the Global Burden of Disease study, the Institutional Review Board of the University "
    "of Washington reviewed and approved the waiver of informed consent. For the Global Dietary Database, individual surveys "
    "underwent the ethical review required by the applicable local context. The present secondary analysis was therefore "
    "exempt from further institutional review, and the requirement for informed consent was waived.", no_sup=True)
add("Author contributions: 【请按 CRediT 填写：Conceptualization, Methodology, Formal analysis, Writing – original draft, "
    "Writing – review & editing 等，并对应到各作者】", italic=True, no_sup=True)

# ==================== 9. SUPPLEMENTARY MATERIAL ====================
H("Supplementary Material")
add("Supplementary Methods. Supplementary Methods S1 (model specification, software versions and random seeds).", no_sup=True)
add("Supplementary Tables. Supplementary Table S1 (internal arithmetic consistency check, 104 stratum–year combinations); "
    "Supplementary Table S2 (correspondence of the eight dietary exposures between the Global Dietary Database and the GBD 2023 "
    "risk framework); Supplementary Table S3 (bootstrap distributions of SHAP importance values); Supplementary Table S4 "
    "(permutation importance on held-out countries); Supplementary Table S5 (quadrant classification under two cut-points).",
    no_sup=True)
add("Supplementary File (PDF). STROBE checklist for this study. 【请把 STROBE 清单作为补充材料 PDF 一并提交】",
    italic=True, no_sup=True)

# ==================== 10. REFERENCES ====================
new.add_page_break()
H("References")
i0 = P15.index("References")
refs = [t for t in P15[i0+1:] if re.match(r"^\s*\d+\.\s", t)]
for r in refs:
    add(r.replace(" (accessed October 12, 2026)", ", accessed October 12, 2026"), no_sup=True)

# ==================== FIGURE LEGENDS（References 之后） ====================
new.add_page_break()
H("Figure Legends")
LEGENDS = [
 ("Figure 1.", "Global trends in dietary exposures and type 2 diabetic kidney disease burden, 1990–2018. "
  "(a–h) Regional trends in eight dietary factors (dashed black line, unweighted mean across countries). "
  "(i, j) Regional trends in the age-standardized incidence rate and disability-adjusted life year rate of type 2 diabetic "
  "kidney disease."),
 ("Figure 2.", "Relative importance of dietary exposures for type 2 diabetic kidney disease incidence and disability "
  "(random forest regression). SHAP (SHapley Additive exPlanations) beeswarm plots for (a) incidence and (b) disability; "
  "features are ordered by mean absolute SHAP value. Colour indicates the feature value (red, high; blue, low). SHAP values "
  "indicate each feature's contribution to the model output and are not effect sizes or causal estimates. The x-axes are on "
  "outcome-specific scales."),
 ("Figure 3.", "Dietary exposures, type 2 diabetic kidney disease burden and the Socio-demographic Index. (a–c) Association of "
  "the Socio-demographic Index with sodium, sugar-sweetened beverages and beans or legumes in 1990 and 2018. (d) Age-standardized "
  "disability-adjusted life year rate versus the Socio-demographic Index in 2018 (204 countries), with a LOWESS curve; colour "
  "indicates the official quintile. Panel d uses the full 204-country sample, whereas panels a–c use the 185 countries with "
  "dietary data."),
 ("Figure 4.", "Attributable burden of type 2 diabetic kidney disease to six dietary risks by Socio-demographic Index quintile "
  "and super-region, 1990–2023. (a) Attributable disability-adjusted life year rate by quintile and (b) by super-region (dashed "
  "grey line, Global). (c) Attributable fraction by quintile in 2023, stacked by dietary risk; bold numbers are the arithmetic "
  "sum of the six risk-specific attributable fractions, which is not a directly estimated joint attributable fraction. "
  "(d) Attributable fraction for each dietary risk with 95% uncertainty intervals in 2023, by quintile."),
 ("Figure 5.", "Descriptive comparison of total type 2 diabetic kidney disease burden and summed risk-specific dietary "
  "attributable fractions. Attributable rate = total burden rate × sum of six risk-specific dietary attributable fractions; this "
  "is a descriptive (not a new statistical) relationship. (a, b) Each point is one Socio-demographic Index quintile or "
  "super-region in 2023; dotted lines mark the global values and the shaded quadrant marks settings with both a high total burden "
  "and a high sum of risk-specific attributable fractions. (c, d) Trajectories of the total disability-adjusted life year rate and "
  "of the summed risk-specific attributable fractions by quintile, 1990–2023."),
]
for h, d_ in LEGENDS:
    p = new.add_paragraph(); p.paragraph_format.line_spacing = 2.0
    r = p.add_run(h + " "); r.bold = True; r.font.size = Pt(12)
    r2 = p.add_run(d_); r2.font.size = Pt(12)

# ==================== TABLES（References 之后，无竖线） ====================
new.add_page_break()
H("Tables")

def make_table(headers, rows, fs=9):
    t = new.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    # 去掉竖线：只保留横线
    tblPr = t._tbl.tblPr
    borders = tblPr.makeelement(qn('w:tblBorders'), {})
    for edge in ("top","left","bottom","right","insideH","insideV"):
        el = borders.makeelement(qn('w:'+edge), {})
        el.set(qn('w:val'), "single" if edge in ("top","bottom","insideH") else "none")
        el.set(qn('w:sz'), "4"); el.set(qn('w:color'), "000000")
        borders.append(el)
    tblPr.append(borders)
    for i,h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text=""
        rr = c.paragraphs[0].add_run(str(h)); rr.bold=True; rr.font.size=Pt(fs)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text=""
            rr = cells[i].paragraphs[0].add_run(str(v)); rr.font.size=Pt(fs)
    return t

def ttitle(num, text):
    p = new.add_paragraph(); p.paragraph_format.line_spacing = 2.0
    r = p.add_run(f"Table {num}. {text}"); r.bold = True; r.font.size = Pt(12)
def tfoot(text):
    p = new.add_paragraph(); p.paragraph_format.line_spacing = 2.0
    r = p.add_run(text); r.font.size = Pt(9); r.italic = True

ROOT = r"D:\work"
# Table 1
t1 = pd.read_csv(f"{ROOT}\\Table1_baseline_by_quintile.csv")
QS = [q.replace(" SDI","") for q in t1["SDI quintile (2023)"]]
LAB = [("n countries","n countries"),("SDI (2018)","SDI (2018)"),("Dietary sodium (mg/d)","Sodium, mg/d"),
       ("SSB (g/d)","SSB, g/d"),("Unprocessed red meat (g/d)","Unprocessed red meat, g/d"),
       ("Processed meat (g/d)","Processed meat, g/d"),("Whole grains (g/d)","Whole grains, g/d"),
       ("Refined grains (g/d)","Refined grains, g/d"),("Beans & legumes (g/d)","Beans or legumes, g/d"),
       ("Fruits (g/d)","Fruits, g/d"),("ASIR","ASIR, per 100 000"),("DALY_rate","DALY rate, per 100 000")]
ttitle(1, "Country-level dietary exposures and type 2 diabetic kidney disease burden by Socio-demographic Index quintile, 2018")
make_table(["Characteristic"]+QS, [[lab]+[str(t1.iloc[i][col]) for i in range(len(t1))] for col,lab in LAB])
tfoot("Values are unweighted country-level means ± standard deviations and should not be interpreted as population-weighted "
      "estimates. Quintiles are the official GBD 2023 threshold-based classification applied to the 185 countries with Global "
      "Dietary Database data. ASIR, age-standardized incidence rate; DALY, disability-adjusted life year; SSB, sugar-sweetened beverage.")
new.add_paragraph()

# Table 2A / 2B
hm = pd.read_csv(f"{ROOT}\\_honest_metrics.csv")
def v(t,cv,c):
    s = hm[(hm.target==t)&(hm.cv==cv)][c].dropna(); return float(s.iloc[0])
ttitle("2A", "Model performance under country-grouped cross-validation")
make_table(["Outcome","Coefficient of determination (GroupKFold)","Coefficient of determination (LOCO)","RMSE, per 100 000"],
    [["Incidence (ASIR)", f"{v('ASIR','GroupKFold','R2'):.3f}", f"{v('ASIR','LOCO','R2'):.3f}", f"{v('ASIR','GroupKFold','RMSE'):.1f}"],
     ["Disability (DALY rate)", f"{v('DALY','GroupKFold','R2'):.3f}", f"{v('DALY','LOCO','R2'):.3f}", f"{v('DALY','GroupKFold','RMSE'):.1f}"]])
tfoot("Random forest regression (500 trees, two candidate features per split). Values are computed on pooled out-of-fold "
      "predictions and reflect performance across held-out countries; they should not be interpreted as the proportion of "
      "between-country variance explained by diet alone. LOCO, leave-one-country-out; RMSE, root-mean-square error.")
new.add_paragraph()

shapA = pd.read_csv(f"{ROOT}\\_reg_shap_ASIR.csv"); shapD = pd.read_csv(f"{ROOT}\\_reg_shap_DALY.csv")
permA = pd.read_csv(f"{ROOT}\\_reg_perm_ASIR.csv"); permD = pd.read_csv(f"{ROOT}\\_reg_perm_DALY.csv")
stA = pd.read_csv(f"{ROOT}\\_rank_stability_ASIR.csv", index_col=0)
stD = pd.read_csv(f"{ROOT}\\_rank_stability_DALY_rate.csv", index_col=0)
ra={f:i+1 for i,f in enumerate(shapA["feature"])}; rd={f:i+1 for i,f in enumerate(shapD["feature"])}
pa={f:i+1 for i,f in enumerate(permA["feature"])}; pd_={f:i+1 for i,f in enumerate(permD["feature"])}
ttitle("2B", "Dietary feature importance (rank) and rank stability under 100 country-level bootstrap resamples")
make_table(["Dietary factor","ASIR: full-data SHAP rank","ASIR: full-data permutation rank","ASIR: % top-3ᵃ",
            "DALY: full-data SHAP rank","DALY: full-data permutation rank","DALY: % top-3ᵃ"],
    [[f, ra[f], pa.get(f,""), f"{stA.loc[f,'pct_top3']:.0f}" if f in stA.index else "",
      rd.get(f,""), pd_.get(f,""), f"{stD.loc[f,'pct_top3']:.0f}" if f in stD.index else ""] for f in shapA["feature"]])
tfoot("Rank 1 = most important. ᵃPercentage of 100 country-level bootstrap resamples in which the factor ranked among the three "
      "most important. SHAP and permutation ranks are from the model fitted to all observations (full-data, in-sample "
      "interpretation); held-out permutation importance is reported in Supplementary Table S4.")
new.add_paragraph()

# Table 3
ui = pd.read_csv(f"{ROOT}\\_cra_ui.csv")
tbb = pd.read_csv(f"{ROOT}\\_total_burden.csv")
tbb = tbb[(tbb.age=="AS")&(tbb.metric=="rate")&(tbb.measure=="DALY")].set_index(["location","year"])["val"]
SDI5=["Low SDI","Low-middle SDI","Middle SDI","High-middle SDI","High SDI"]
REG7=["Sub-Saharan Africa","North Africa and Middle East","South Asia","Southeast Asia, East Asia, and Oceania",
      "Central Europe, Eastern Europe, and Central Asia","Latin America and Caribbean","High-income"]
ttitle(3, "Age-standardized attributable burden of type 2 diabetic kidney disease to six dietary risks, by "
          "Socio-demographic Index quintile and super-region")
rows=[]
lab="SDI quintile"
for loc in SDI5+["Global"]:
    r90=ui[(ui.location==loc)&(ui.year==1990)].iloc[0]; r23=ui[(ui.location==loc)&(ui.year==2023)].iloc[0]
    rows.append([lab,loc,f"{r90.attr:.1f}",f"{r23.attr:.1f}",f"{(r23.attr/r90.attr-1)*100:+.1f}",
                 f"{r23.paf:.1f}",f"{tbb.loc[(loc,1990)]:.1f}",f"{tbb.loc[(loc,2023)]:.1f}"]); lab=""
lab="Super-region"
for loc in REG7+["Global"]:
    r90=ui[(ui.location==loc)&(ui.year==1990)].iloc[0]; r23=ui[(ui.location==loc)&(ui.year==2023)].iloc[0]
    rows.append([lab,loc,f"{r90.attr:.1f}",f"{r23.attr:.1f}",f"{(r23.attr/r90.attr-1)*100:+.1f}",
                 f"{r23.paf:.1f}",f"{tbb.loc[(loc,1990)]:.1f}",f"{tbb.loc[(loc,2023)]:.1f}"]); lab=""
make_table(["Stratum","Location","Attributable DALY rate, 1990","Attributable DALY rate, 2023","Δ%",
            "Sum of risk-specific PAFs, 2023, %ᵃ","Total DALY rate, 1990","Total DALY rate, 2023"], rows, fs=8.5)
tfoot("All rates are age-standardized and expressed per 100 000 population. ᵃArithmetic sum of six individual risk-specific "
      "attributable fractions, reported as an aggregate of risk-specific estimates; it is not a directly estimated joint "
      "attributable fraction. Percentage changes were computed from unrounded estimates. DALY, disability-adjusted life year; "
      "PAF, population attributable fraction.")
new.add_paragraph()

# Table 4
t4 = pd.read_csv(f"{ROOT}\\Table4_PAF_by_risk_SDI.csv")
ttitle(4, "Attributable fraction (%) of type 2 diabetic kidney disease to each dietary risk by Socio-demographic Index quintile "
          "in 2023 (95% uncertainty interval)")
make_table(list(t4.columns), [[str(x).replace("(-0.0","(0.0") for x in row] for row in t4.values.tolist()], fs=8.5)
tfoot("Individual attributable fractions as provided by the Global Burden of Disease comparative risk assessment; risks may "
      "overlap, so they should not be summed to obtain a joint attributable fraction. Lower bounds shown as 0.0 correspond to "
      "floating-point noise around zero.")
new.add_paragraph()

# Table 5
mc = pd.read_csv(f"{ROOT}\\_model_comparison2.csv").pivot(index="model", columns="outcome")
ttitle(5, "Explanatory performance of four feature combinations under country-grouped cross-validation")
r5=[]
for mdl,feats in [("year only","Year only"),("year + SDI","Year + Socio-demographic Index"),
                  ("year + SDI + diet","Year + Socio-demographic Index + eight dietary exposures"),
                  ("diet only","Eight dietary exposures only")]:
    r5.append([mdl,feats,f"{mc.loc[mdl,('R2','ASIR')]:.3f}",f"{mc.loc[mdl,('RMSE','ASIR')]:.2f}",
               f"{mc.loc[mdl,('R2','DALY_rate')]:.3f}",f"{mc.loc[mdl,('RMSE','DALY_rate')]:.2f}"])
make_table(["Model","Features","ASIR coefficient of determination","ASIR RMSE","DALY coefficient of determination","DALY RMSE"], r5, fs=8.5)
tfoot("All models use the same country-grouped (5-fold) splits. Every model used the same hyperparameters (500 trees, two "
      "candidate features per split, bootstrap enabled); the comparisons are descriptive of predictive performance rather than "
      "isolated incremental causal contributions. RMSE is in units per 100 000.")
new.add_paragraph()

# ==================== DATA SHARING STATEMENT ====================
new.add_page_break()
H("Data sharing statement")
add("The data analysed in this study are openly available from the Global Dietary Database "
    "(https://www.globaldietarydatabase.org) and the Global Burden of Disease Study 2023 results tool "
    "(https://vizhub.healthdata.org/gbd-results/). The derived datasets and the analysis code used to generate the results are "
    "available in a public repository at 【请填 GitHub/Zenodo URL】.", no_sup=True)

print("SAVED", OUT)
new.save(OUT)
