# Pre-specified design: overlapping returns and evidence

Registered 2026-10-20, before downloading or examining study results.

## Decision and falsifiable question
Before treating a strong historical average as allocation evidence, does counting
daily overlapping 21-session factor P&Ls as independent materially overstate the
precision of the mean? Hypothesis: overlap increases naive absolute t-statistics,
while dependence-aware intervals and disjoint windows reveal much less evidence.
Null and mixed results will be reported for all four factors, without selecting a winner.

## Data and universe
Kenneth French Data Library daily US Mkt-RF, SMB, HML and Mom. Download current
snapshot with SHA-256 and retrieval timestamp. Restrict 1970-01-01 through
2025-12-31, using complete common dates. Raw returns are in percent; divide by 100.
Current-vintage research factors, not a point-in-time tradable reconstruction.

## Timing and estimand
No fitted signal and no trade simulation. For every eligible start date t,
sum the following h daily factor returns, inclusive of t, as constant-notional
factor P&L. This is an arithmetic sum, not a compounded investment return.
Compare the mean to zero using iid SE and Newey-West/Bartlett HAC SE.
The same overlapping sample and same mean are used for both estimates.
These are unconditional factor-premium diagnostics, not alpha tests.

## Chronological protocol
1970-1999 historical reference; 2000-2019 first evaluation; 2020-2025 later
replication. Primary reported interval is combined evaluation 2000-2025,
with the two fixed chronological slices reported separately, no tuning.
Form windows entirely within each period; never cross boundaries.
Primary horizon h=21 and HAC bandwidth L=63. No model selection.
Naive t = mean/(sample SD/sqrt(N)). HAC uses demeaned covariance with 1/N
normalization, Bartlett weights 1-k/(L+1), finite-sample N/(N-1) correction.
Intervals: mean +/- 1.96 SE, asymptotic and descriptive.

## Sensitivity and independent checks
- Horizons 1, 5, 10, 21 and 63 sessions; HAC bandwidth 3h.
- At h=21, bandwidths 20, 42, 63 and 126; shorter bandwidth can undercorrect.
- Non-overlapping h=21 windows at every one of 21 possible start offsets;
  do not select the most favorable offset, report every offset and its range.
- Circular moving-block bootstrap of underlying daily returns, 2,000 draws,
  block lengths 21, 63, 126 sessions, fixed seed 20261020. Re-form windows
  on each resample. These are resampled scenarios, not new observed histories.
- Independently recompute headline mean/SE/t from saved window CSV and verify
  HAC with a separate Toeplitz-style covariance calculation and statsmodels.
- Check complete dates, finite values, unique dates, period boundary exclusion.

## Limits
Asymptotic t-statistics are not guaranteed calibrated in finite, nonstationary
samples; block length and HAC bandwidth matter. No multiple-testing adjustment,
no causal or forward profitability claims, no transaction costs, no newly
discovered strategy. Real daily serial dependence and heteroskedasticity can
add to or offset overlap. Sqrt(h) is an iid theoretical reference only.
Non-overlap avoids shared days but does not eliminate economic dependence.
Do not equate variance-equivalent sample size with a literal count of independent bets.
