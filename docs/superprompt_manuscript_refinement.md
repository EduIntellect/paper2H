# AUTOCONTENT INSTRUCTION PROMPT: FULL MANUSCRIPT ALIGNMENT (paper2H)
## Target File: `paper/paper2_submission.tex`

You are an expert academic writer and a senior LaTeX editor. Your task is to audit and update the LaTeX manuscript at `paper/paper2_submission.tex` in the current workspace. You must ensure it incorporates all 5 tabular models (Ridge, LightGBM, ExtraTrees, KNN, MLP) plus ARIMA(2,0,0) robustness results across the six domains (PM2.5, Load, Wind, Traffic, PM10 Madrid, PM10 Barcelona), and align all text and tables with the authoritative data below.

Use your file-editing tools (like `replace_file_content` or similar) to perform these edits directly on `paper/paper2_submission.tex`.

---

## 1. AUTHORITATIVE DATA SOURCE OF TRUTH

### Table 3 Master Results (H* Descriptors & DM Significance)
Use these exact numbers for Table 3 (`tab:results`):
- **PM2.5 (Beijing):**
  - Ridge: H*(relax)=48, H*(strict)=40, interval=[9, 48], DM sig=58.3%, Profile=FRAGMENTED
  - LightGBM: H*(relax)=48, H*(strict)=19, interval=[30, 48], DM sig=35.4%, Profile=FRAGMENTED
  - ExtraTrees: H*(relax)=48, H*(strict)=26, interval=[23, 48], DM sig=37.5%, Profile=DELAYED_CONTIGUOUS
  - KNN: H*(relax)=48, H*(strict)=16, interval=[33, 48], DM sig=37.5%, Profile=FRAGMENTED
  - MLP: H*(relax)=48, H*(strict)=36, interval=[13, 48], DM sig=37.5%, Profile=DELAYED_CONTIGUOUS
- **Electric Load (UCI):**
  - Ridge: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=0.0%, Profile=SUSTAINED
  - LightGBM: H*(relax)=0, H*(strict)=0, interval=[—, —], DM sig=0.0%, Profile=IMMEDIATE_COLLAPSE
  - ExtraTrees: H*(relax)=0, H*(strict)=0, interval=[—, —], DM sig=0.0%, Profile=IMMEDIATE_COLLAPSE
  - KNN: H*(relax)=0, H*(strict)=0, interval=[—, —], DM sig=100.0%, Profile=IMMEDIATE_COLLAPSE (significantly worse)
  - MLP: H*(relax)=0, H*(strict)=0, interval=[—, —], DM sig=100.0%, Profile=IMMEDIATE_COLLAPSE (significantly worse) [a]
- **Wind Speed (NREL):**
  - Ridge: H*(relax)=48, H*(strict)=48, interval=[1, 48], DM sig=100.0%, Profile=SUSTAINED
  - LightGBM: H*(relax)=48, H*(strict)=48, interval=[1, 48], DM sig=72.9%, Profile=SUSTAINED
  - ExtraTrees: H*(relax)=48, H*(strict)=47, interval=[2, 48], DM sig=83.3%, Profile=FRAGMENTED
  - KNN: H*(relax)=48, H*(strict)=47, interval=[2, 48], DM sig=85.4%, Profile=FRAGMENTED
  - MLP: H*(relax)=48, H*(strict)=47, interval=[2, 48], DM sig=95.8%, Profile=FRAGMENTED
  - ARIMA(2,0,0): H*(relax)=48, H*(strict)=48, interval=[1, 48], DM sig=89.6%, Profile=SUSTAINED
- **Traffic Flow (METR-LA):**
  - Ridge: H*(relax)=72, H*(strict)=5, interval=[63, 67], DM sig=13.9%, Profile=FRAGMENTED
  - LightGBM: H*(relax)=72, H*(strict)=4, interval=[64, 67], DM sig=4.2%, Profile=FRAGMENTED
  - ExtraTrees: H*(relax)=72, H*(strict)=4, interval=[64, 67], DM sig=4.2%, Profile=FRAGMENTED
  - KNN: H*(relax)=72, H*(strict)=6, interval=[64, 69], DM sig=2.8%, Profile=FRAGMENTED
  - MLP: H*(relax)=66, H*(strict)=3, interval=[40, 42], DM sig=9.7%, Profile=FRAGMENTED
  - ARIMA(2,0,0): H*(relax)=70, H*(strict)=9, interval=[52, 60], DM sig=22.2%, Profile=FRAGMENTED
- **PM10 Madrid (Casa de Campo):**
  - Ridge: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=85.7%, Profile=SUSTAINED
  - LightGBM: H*(relax)=7, H*(strict)=6, interval=[2, 7], DM sig=85.7%, Profile=DELAYED_CONTIGUOUS
  - ExtraTrees: H*(relax)=7, H*(strict)=6, interval=[2, 7], DM sig=71.4%, Profile=DELAYED_CONTIGUOUS
  - KNN: H*(relax)=7, H*(strict)=6, interval=[2, 7], DM sig=71.4%, Profile=DELAYED_CONTIGUOUS
  - MLP: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=85.7%, Profile=SUSTAINED
- **PM10 Barcelona (Eixample):**
  - Ridge: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=100.0%, Profile=SUSTAINED
  - LightGBM: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=85.7%, Profile=SUSTAINED
  - ExtraTrees: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=85.7%, Profile=SUSTAINED
  - KNN: H*(relax)=7, H*(strict)=6, interval=[2, 7], DM sig=100.0%, Profile=DELAYED_CONTIGUOUS
  - MLP: H*(relax)=7, H*(strict)=7, interval=[1, 7], DM sig=100.0%, Profile=SUSTAINED

*Note [a]: MLP on Load exhibits numerical instability due to unscaled MW-range targets, yielding skill scores from -16 to -38.*

---

## 2. LATEX REPLACEMENT TEMPLATES

### Table 3: Main Results (`tab:results`)
Locate `\begin{table}[ht]` representing Table 3 and ensure it matches the following structure:
```latex
\begin{table}[ht]
\centering
\caption{H* descriptors and DM significance for all 32 (model, domain)
combinations. \Hrelax: last horizon with positive skill (gaps allowed).
\Hstrict: length of the longest contiguous positive-skill run.
$h_s$--$h_e$: start and end of that run.
\% DM: proportion of horizons significant at BH-corrected $\alpha=0.05$.
$\dagger$~100\,\% DM significant but \emph{worse} than persistence (negative skill).}
\label{tab:results}
\scriptsize
\setlength{\tabcolsep}{2.6pt}
\renewcommand{\arraystretch}{1.12}
\begin{tabularx}{\textwidth}{llrrrrlX}
\toprule
Domain & Model & \Hrelax & \Hstrict & $h_s$ & $h_e$ & \% DM & Profile \\
\midrule
\multirow{5}{*}{\shortstack[l]{PM$_{2.5}$\\(hrly)}}
  & Ridge      & 48 & 40 &  9 & 48 & 58.3\% & \textsc{fragmented} \\
  & LightGBM   & 48 & 19 & 30 & 48 & 35.4\% & \textsc{fragmented} \\
  & ExtraTrees & 48 & 26 & 23 & 48 & 37.5\% & \textsc{delayed\_contiguous} \\
  & KNN        & 48 & 16 & 33 & 48 & 37.5\% & \textsc{fragmented} \\
  & MLP        & 48 & 36 & 13 & 48 & 37.5\% & \textsc{delayed\_contiguous} \\
\midrule
\multirow{5}{*}{\shortstack[l]{Load\\(daily)}}
  & Ridge      &  7 &  7 &  1 &  7 &   0.0\%           & \textsc{sustained} \\
  & LightGBM   &  0 &  0 & ---& ---&   0.0\%           & \textsc{immediate\_collapse} \\
  & ExtraTrees &  0 &  0 & ---& ---&   0.0\%           & \textsc{immediate\_collapse} \\
  & KNN        &  0 &  0 & ---& ---& 100.0\%$^\dagger$ & \textsc{immediate\_collapse} \\
  & MLP        &  0 &  0 & ---& ---& 100.0\%$^\dagger$ & \textsc{immediate\_collapse} \\
\midrule
\multirow{6}{*}{\shortstack[l]{Wind\\(hrly)}}
  & Ridge        & 48 & 48 &  1 & 48 & 100.0\% & \textsc{sustained} \\
  & LightGBM     & 48 & 48 &  1 & 48 &  72.9\% & \textsc{sustained} \\
  & ExtraTrees   & 48 & 47 &  2 & 48 &  83.3\% & \textsc{fragmented} \\
  & KNN          & 48 & 47 &  2 & 48 &  85.4\% & \textsc{fragmented} \\
  & MLP          & 48 & 47 &  2 & 48 &  95.8\% & \textsc{fragmented} \\
  & ARIMA(2,0,0) & 48 & 48 &  1 & 48 &  89.6\% & \textsc{sustained} \\
\midrule
\multirow{6}{*}{\shortstack[l]{Traffic\\(hrly)}}
  & Ridge        & 72 &  5 & 63 & 67 &  13.9\% & \textsc{fragmented} \\
  & LightGBM     & 72 &  4 & 64 & 67 &   4.2\% & \textsc{fragmented} \\
  & ExtraTrees   & 72 &  4 & 64 & 67 &   4.2\% & \textsc{fragmented} \\
  & KNN          & 72 &  6 & 64 & 69 &   2.8\% & \textsc{fragmented} \\
  & MLP          & 66 &  3 & 40 & 42 &   9.7\% & \textsc{fragmented} \\
  & ARIMA(2,0,0) & 70 &  9 & 52 & 60 &  22.2\% & \textsc{fragmented} \\
\midrule
\multirow{5}{*}{\shortstack[l]{PM10\\Madrid}}
  & Ridge      & 7 & 7 & 1 & 7 &  85.7\% & \textsc{sustained} \\
  & LightGBM   & 7 & 6 & 2 & 7 &  85.7\% & \textsc{delayed\_contiguous} \\
  & ExtraTrees & 7 & 6 & 2 & 7 &  71.4\% & \textsc{delayed\_contiguous} \\
  & KNN        & 7 & 6 & 2 & 7 &  71.4\% & \textsc{delayed\_contiguous} \\
  & MLP        & 7 & 7 & 1 & 7 &  85.7\% & \textsc{sustained} \\
\midrule
\multirow{5}{*}{\shortstack[l]{PM10\\Barcelona}}
  & Ridge      & 7 & 7 & 1 & 7 & 100.0\% & \textsc{sustained} \\
  & LightGBM   & 7 & 7 & 1 & 7 &  85.7\% & \textsc{sustained} \\
  & ExtraTrees & 7 & 7 & 1 & 7 &  85.7\% & \textsc{sustained} \\
  & KNN        & 7 & 6 & 2 & 7 & 100.0\% & \textsc{delayed\_contiguous} \\
  & MLP        & 7 & 7 & 1 & 7 & 100.0\% & \textsc{sustained} \\
\bottomrule
\end{tabularx}
\end{table}
```

---

## 3. AUDIT & REWRITE INSTRUCTIONS

Read `paper/paper2_submission.tex` completely and ensure the following points are correctly written and synchronized:

1. **Introduction & Abstract:** Must state clearly that the work evaluates 5 model classes (Ridge, LightGBM, ExtraTrees, KNN, MLP) and ARIMA(2,0,0) across six domains, defining $H^*(\mathrm{relax})$ and $H^*(\mathrm{strict})$ under rolling-origin validation.
2. **Models Section (§5.2):** Must list all 5 estimators and the ARIMA baseline, and include a note explaining that MLP is excluded from the quantitative Load tables due to scale-induced numerical instability.
3. **PM10 Madrid & Barcelona results:**
   - Verify Madrid has the delayed profile for LightGBM, ExtraTrees, KNN (falling below 0 at $h=1$ and recovering at $h=2$), while Ridge and MLP are fully sustained.
   - Verify Barcelona has Ridge, LightGBM, ExtraTrees, and MLP as fully sustained from $h=1$.
   - Incorporate the ACF lag-1 comparison (Barcelona 0.644 vs. Madrid 0.562, $\Delta = 0.083$) as the physical explanation of the $h=1$ skill difference.
4. **Electric Load results:**
   - Incorporate the statistical power analysis explaining why Ridge has 0.0% DM significance despite a $H^*(\mathrm{strict})=7$ profile (MDE is $\ge 0.061$, twice the maximum observed Ridge skill of 0.030, sample size $n \approx 280$ is underpowered).
5. **Traffic Flow results:**
   - Describe the "ghost-skill" pattern (high $H^*(\mathrm{relax})$, low $H^*(\mathrm{strict})$) and explain it as a dataset periodic cycle artefact of the 72-step METR-LA signal.
6. **Robustness & Limitations:**
   - Discuss ARIMA(2,0,0) as a second model that preserves the morphotype in Wind (everywhere sustained) and partially in Traffic (maintains ghost-skill fragmentation, with the window shifting to $h=52-60$).
   - Discuss ExtraTrees sensitivity (50 trees vs 100 trees on PM10 Madrid showing mean skill difference of just 0.006, leaving all profiles unchanged).

Execute the necessary edits and report a summary of changes when finished.
