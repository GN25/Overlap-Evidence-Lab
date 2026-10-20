"""Independent recomputation from saved outputs; run after research.py."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

P = Path(__file__).resolve().parent
daily = pd.read_csv(P/'data/daily_factors.csv', index_col=0, parse_dates=True)
windows = pd.read_csv(P/'results/primary_windows.csv', parse_dates=['start','end'])
stats = pd.read_csv(P/'results/statistics.csv')
primary = stats.query("period == 'evaluation_2000_2025' and horizon == 21 and hac_lag == 63").set_index('factor')
checks = []
for factor, g in windows.groupby('factor', sort=False):
    y = g.pnl.to_numpy()
    n = len(y)
    fit = sm.OLS(y, np.ones((n,1))).fit(cov_type='HAC', cov_kwds={'maxlags':63,'use_correction':True})
    z = y-y.mean()
    # Independent quadratic form for Bartlett covariance, no analysis function imported.
    weighted_cross = sum((1-k/64) * np.dot(z[:-k],z[k:]) for k in range(1,64))
    se = np.sqrt((np.dot(z,z)+2*weighted_cross)/(n*(n-1)))
    r = primary.loc[factor]
    np.testing.assert_allclose([y.mean(),y.std(ddof=1)/np.sqrt(n),se], [r['mean'],r.se_iid,r.se_hac], rtol=1e-9)
    np.testing.assert_allclose(fit.bse[0],se,rtol=1e-12)
    # Recompute every forward window by explicit date-slice summation.
    direct = np.array([daily.loc[a:b,factor].sum() for a,b in zip(g.start,g.end)])
    np.testing.assert_allclose(direct,y,rtol=1e-8,atol=1e-11)
    assert g.start.min() >= pd.Timestamp('2000-01-01')
    assert g.end.max() <= pd.Timestamp('2025-12-31')
    assert (g.end>g.start).all() and g.start.is_unique
    checks.append(dict(factor=factor,n=n,mean=float(y.mean()),
        t_iid=float(y.mean()/(y.std(ddof=1)/np.sqrt(n))),t_hac=float(fit.tvalues[0]),
        statsmodels_se=float(fit.bse[0]),all_windows_recomputed=True))

for block in [21,63,126]:
    boot=pd.read_csv(P/f'results/bootstrap_means_block{block}.csv')
    summ=pd.read_csv(P/'results/bootstrap_summary.csv').query('block == @block').set_index('factor')
    assert len(boot)==2000
    np.testing.assert_allclose(boot.std(ddof=1),summ.loc[boot.columns,'bootstrap_se'],rtol=1e-12)

offsets=pd.read_csv(P/'results/nonoverlap_offsets.csv')
assert offsets.groupby(['period','factor']).size().eq(21).all()
# Constant and impulse checks pin down forward endpoints and no compounding.
from research import window_sum
np.testing.assert_allclose(window_sum(np.ones((30,2))*.01,21),.21)
impulse=np.zeros((50,1)); impulse[25]=1
assert window_sum(impulse,21).sum()==21

out=dict(status='passed',checks=checks,notes=[
    'Every primary forward window recomputed from saved daily data',
    'Independent HAC quadratic form agrees with statsmodels',
    'Bootstrap saved draws and all 21 nonoverlap offsets checked'])
(P/'results/verification.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
