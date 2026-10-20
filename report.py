from pathlib import Path
import json
import platform
import numpy
import pandas as pd
import matplotlib
import statsmodels

P=Path(__file__).resolve().parent
s=pd.read_csv(P/'results/statistics.csv')
b=pd.read_csv(P/'results/bootstrap_summary.csv')
o=pd.read_csv(P/'results/nonoverlap_offsets.csv')
def table(df):
    # No optional tabulate dependency.
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in df.itertuples(index=False,name=None))

primary=s.query("period=='evaluation_2000_2025' and horizon==21 and hac_lag==63").copy()
t=primary[['factor','n_windows','mean','t_iid','t_hac','se_ratio']].copy()
t['mean']=t['mean'].map(lambda x:f'{x:.4%}')
for c in ['t_iid','t_hac','se_ratio']: t[c]=t[c].map(lambda x:f'{x:.3f}')
chunks=['# Results\n\nAll values below are computed from saved outputs. No factor is omitted.\n',
'## Primary evaluation: 2000-01-03 through 2025-12-31\n\n'+table(t),
'\nThe sample contains 6,539 daily rows and 6,519 complete 21-session windows per factor.\n'
'All four naive t-statistics exceed 1.96; only market excess does with the primary\n'
'dependence-aware SE. This is a descriptive comparison, not four strategy discoveries.\n'
'The economic mean is identical across the two methods. Multiplicity is unadjusted.\n',
'## Bandwidth sensitivity\n\n'+table(s.query("period=='evaluation_2000_2025' and horizon==21")[['factor','hac_lag','t_hac']].round(3)),
'\nFor all four tested bandwidths, market excess remains above 1.96 and all other\n'
'factors remain below it. Bandwidth choices still change uncertainty materially.\n',
'## Fixed chronological slices (21 sessions, 63 lags)\n\n'+table(s.query('horizon==21 and hac_lag==63')[['period','factor','t_iid','t_hac','se_ratio']].round(3)),
'\nThe historical reference gives momentum a HAC t-statistic of 4.43, so this study\n'
'cannot support a claim that momentum never earned a premium. The later 2020-2025\n'
'slice already has a weak naive momentum t-statistic. Period choice matters.\n',
'## All disjoint-window offsets\n\n'+table(o.query("period=='evaluation_2000_2025'").groupby('factor').agg(n_min=('n','min'),n_max=('n','max'),t_min=('t','min'),t_median=('t','median'),t_max=('t','max')).reset_index().round(3)),
'\nEvery possible offset is retained. These t-statistics assume independence between\n'
'non-overlapping windows; no shared daily returns does not guarantee no dependence.\n',
'## Resampling sensitivity\n\n'+table(b.round(6)),
'\nCircular moving-block bootstrap resamples real daily rows jointly across factors,\n'
'then re-forms 21-session windows, with 2,000 draws per block length. Percentile\n'
'intervals are resampling results, not observations or exact coverage guarantees.\n'
'All tested block lengths include zero for SMB, HML and Mom and exclude zero for\n'
'market excess. Bootstrap validity assumes sufficient stability of dependence.\n',
'## Interpretation and limits\n\n'
'Adjacent windows share 20 of 21 daily returns by construction. This design\n'
'demonstrates precision inflation in an unconditional arithmetic-mean test.\n'
'It does not estimate predictive alpha, transaction costs, trading capacity or\n'
'implementable net performance. Current-vintage factor definitions and historical\n'
'revisions limit real-time interpretation. Summed P&L uses constant daily notional;\n'
'it is not compounded factor wealth. Do not apply these numerical multipliers\n'
'automatically to predictive regressions: residual dependence can differ.\n'
'HAC and bootstrap inference remain approximate under heteroskedasticity,\n'
'nonstationarity and fat tails. The sqrt(h) line is an iid limiting reference;\n'
'the finite-bandwidth Bartlett estimator need not equal it even under iid daily\n'
'returns. No claim about false-positive rates is estimated here.\n',
'## Verification\n\nSee [verification.json](verification.json). Every primary 21-session P&L was\n'
'independently reconstructed from the saved daily CSV. A separate covariance\n'
'quadratic form and statsmodels OLS HAC agree with all headline statistics.\n'
'Saved bootstrap draws and non-overlap offsets were also checked.\n']
(P/'results/report.md').write_text('\n\n'.join(chunks))
(P/'results/environment.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__,pandas=pd.__version__,matplotlib=matplotlib.__version__,statsmodels=statsmodels.__version__),indent=2))
print('Wrote computed report and environment record.')
