"""Fixed, reproducible inference experiment. See RESEARCH_DESIGN.md first."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
FACTORS = ['Mkt-RF', 'SMB', 'HML', 'Mom']
PERIODS = {
    'reference_1970_1999': ('1970-01-01', '1999-12-31'),
    'evaluation_2000_2019': ('2000-01-01', '2019-12-31'),
    'replication_2020_2025': ('2020-01-01', '2025-12-31'),
    'evaluation_2000_2025': ('2000-01-01', '2025-12-31'),
}
SOURCES = {
    'ff3_daily': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
    'mom_daily': 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare_data(download=False):
    out = ROOT / 'data/daily_factors.csv'
    if out.exists() and not download:
        return pd.read_csv(out, index_col=0, parse_dates=True)
    frames, manifest = [], []
    for name, url in SOURCES.items():
        path = ROOT / f'data/raw/{name}.zip'
        path.parent.mkdir(parents=True, exist_ok=True)
        if download or not path.exists():
            urllib.request.urlretrieve(url, path)
        with zipfile.ZipFile(path) as z:
            raw = z.read(z.namelist()[0]).decode('utf-8-sig')
        rows = [line for line in raw.splitlines() if re.match(r'^\s*\d{8},', line)]
        columns = ['date', 'Mkt-RF', 'SMB', 'HML', 'RF'] if name == 'ff3_daily' else ['date', 'Mom']
        df = pd.read_csv(io.StringIO('\n'.join(rows)), names=columns)
        df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')
        frames.append(df.set_index('date') / 100)
        manifest.append(dict(url=url, raw_sha256=sha(path), file=path.name,
                             retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                             source_header=raw.splitlines()[:5]))
    data = frames[0][['Mkt-RF', 'SMB', 'HML']].join(frames[1], how='inner').loc['1970':'2025', FACTORS]
    assert data.index.is_unique and data.index.is_monotonic_increasing
    assert data.notna().all().all() and np.isfinite(data.to_numpy()).all()
    assert (data.abs() < 0.99).all().all(), 'Missing return codes or implausible units'
    data.to_csv(out, float_format='%.10f')
    (ROOT / 'data/manifest.json').write_text(json.dumps(dict(
        sources=manifest, daily_csv_sha256=sha(out), units='decimal daily factor returns',
        snapshot_caveat='Current revised research-factor snapshot; not point-in-time constituents',
        first_date=str(data.index[0].date()), last_date=str(data.index[-1].date()), rows=len(data)), indent=2))
    return data


def window_sum(x, h):
    """Forward-inclusive arithmetic P&L; each return used h times internally."""
    cs = np.vstack([np.zeros((1, x.shape[1])), np.cumsum(x, axis=0)])
    return cs[h:] - cs[:-h]


def mean_stats(y, lag):
    n = len(y)
    center = y - y.mean(axis=0)
    gamma0 = (center * center).sum(axis=0) / n
    lrv = gamma0.copy()
    for k in range(1, min(lag, n - 1) + 1):
        lrv += 2 * (1 - k / (lag + 1)) * (center[k:] * center[:-k]).sum(axis=0) / n
    iid = np.sqrt(gamma0 / (n - 1))
    hac = np.sqrt(np.maximum(lrv, 0) / (n - 1))
    return y.mean(axis=0), iid, hac


def bootstrap_daily(x, block, draws=2000):
    """Circular block resampling of observed daily rows, shared across factors."""
    rng = np.random.default_rng(20261020 + block)
    n = len(x)
    means = np.empty((draws, x.shape[1]))
    for j in range(draws):
        starts = rng.integers(0, n, size=(n + block - 1) // block)
        idx = ((starts[:, None] + np.arange(block)) % n).ravel()[:n]
        means[j] = window_sum(x[idx], 21).mean(axis=0)
    return means


def run():
    data = prepare_data()
    results = ROOT / 'results'
    results.mkdir(exist_ok=True)
    records, offsets, window_rows = [], [], []
    for period, (lo, hi) in PERIODS.items():
        df = data.loc[lo:hi]
        x = df.to_numpy()
        for h in [1, 5, 10, 21, 63]:
            y = window_sum(x, h)
            lags = sorted(set([3*h] + ([20, 42, 63, 126] if h == 21 else [])))
            for lag in lags:
                mean, iid, hac = mean_stats(y, lag)
                for k, factor in enumerate(FACTORS):
                    records.append(dict(period=period, factor=factor, horizon=h, hac_lag=lag,
                        n_daily=len(x), n_windows=len(y), first_start=str(df.index[0].date()),
                        last_end=str(df.index[-1].date()), mean=mean[k], se_iid=iid[k],
                        se_hac=hac[k], t_iid=mean[k]/iid[k], t_hac=mean[k]/hac[k],
                        se_ratio=hac[k]/iid[k]))
            if h == 21:
                for offset in range(h):
                    disjoint = y[offset::h]
                    # These t statistics still assume independence BETWEEN disjoint windows.
                    m, se, _ = mean_stats(disjoint, 0)
                    for k, factor in enumerate(FACTORS):
                        offsets.append(dict(period=period, factor=factor, offset=offset,
                            n=len(disjoint), mean=m[k], se=se[k], t=m[k]/se[k]))
                if period == 'evaluation_2000_2025':
                    for k, factor in enumerate(FACTORS):
                        window_rows.append(pd.DataFrame(dict(start=df.index[:-20],
                            end=df.index[20:], factor=factor, pnl=y[:, k])))
    pd.DataFrame(records).to_csv(results/'statistics.csv', index=False, float_format='%.12g')
    pd.DataFrame(offsets).to_csv(results/'nonoverlap_offsets.csv', index=False, float_format='%.12g')
    pd.concat(window_rows).to_csv(results/'primary_windows.csv', index=False, float_format='%.12g')
    df = data.loc['2000':'2025']
    boot_records = []
    for block in [21, 63, 126]:
        boot = bootstrap_daily(df.to_numpy(), block)
        pd.DataFrame(boot, columns=FACTORS).to_csv(results/f'bootstrap_means_block{block}.csv', index=False)
        for k, factor in enumerate(FACTORS):
            boot_records.append(dict(factor=factor, block=block, draws=len(boot),
                bootstrap_se=boot[:,k].std(ddof=1),
                percentile_025=np.quantile(boot[:,k], .025),
                percentile_975=np.quantile(boot[:,k], .975)))
    pd.DataFrame(boot_records).to_csv(results/'bootstrap_summary.csv', index=False)
    print(pd.DataFrame(records).query("period == 'evaluation_2000_2025' and horizon == 21 and hac_lag == 63").to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    if args.download:
        prepare_data(download=True)
    run()
