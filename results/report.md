# Results

All values below are computed from saved outputs. No factor is omitted.


## Primary evaluation: 2000-01-03 through 2025-12-31

| factor | n_windows | mean | t_iid | t_hac | se_ratio |
| --- | --- | --- | --- | --- | --- |
| Mkt-RF | 6519 | 0.6808% | 11.185 | 2.808 | 3.983 |
| SMB | 6519 | 0.0817% | 2.169 | 0.549 | 3.951 |
| HML | 6519 | 0.2166% | 4.717 | 1.041 | 4.531 |
| Mom | 6519 | 0.2542% | 3.879 | 0.967 | 4.010 |


The sample contains 6,539 daily rows and 6,519 complete 21-session windows per factor.
All four naive t-statistics exceed 1.96; only market excess does with the primary
dependence-aware SE. This is a descriptive comparison, not four strategy discoveries.
The economic mean is identical across the two methods. Multiplicity is unadjusted.


## Bandwidth sensitivity

| factor | hac_lag | t_hac |
| --- | --- | --- |
| Mkt-RF | 20 | 3.066 |
| SMB | 20 | 0.579 |
| HML | 20 | 1.24 |
| Mom | 20 | 1.031 |
| Mkt-RF | 42 | 2.82 |
| SMB | 42 | 0.54 |
| HML | 42 | 1.08 |
| Mom | 42 | 0.945 |
| Mkt-RF | 63 | 2.808 |
| SMB | 63 | 0.549 |
| HML | 63 | 1.041 |
| Mom | 63 | 0.967 |
| Mkt-RF | 126 | 2.654 |
| SMB | 126 | 0.578 |
| HML | 126 | 0.962 |
| Mom | 126 | 0.942 |


For all four tested bandwidths, market excess remains above 1.96 and all other
factors remain below it. Bandwidth choices still change uncertainty materially.


## Fixed chronological slices (21 sessions, 63 lags)

| period | factor | t_iid | t_hac | se_ratio |
| --- | --- | --- | --- | --- |
| reference_1970_1999 | Mkt-RF | 11.214 | 2.53 | 4.432 |
| reference_1970_1999 | SMB | -1.646 | -0.331 | 4.965 |
| reference_1970_1999 | HML | 12.666 | 2.548 | 4.971 |
| reference_1970_1999 | Mom | 19.823 | 4.432 | 4.473 |
| evaluation_2000_2019 | Mkt-RF | 8.065 | 1.973 | 4.089 |
| evaluation_2000_2019 | SMB | 3.757 | 1.0 | 3.758 |
| evaluation_2000_2019 | HML | 5.894 | 1.271 | 4.638 |
| evaluation_2000_2019 | Mom | 3.56 | 0.864 | 4.12 |
| replication_2020_2025 | Mkt-RF | 7.883 | 2.144 | 3.676 |
| replication_2020_2025 | SMB | -1.877 | -0.424 | 4.422 |
| replication_2020_2025 | HML | 0.726 | 0.169 | 4.295 |
| replication_2020_2025 | Mom | 1.315 | 0.37 | 3.553 |
| evaluation_2000_2025 | Mkt-RF | 11.185 | 2.808 | 3.983 |
| evaluation_2000_2025 | SMB | 2.169 | 0.549 | 3.951 |
| evaluation_2000_2025 | HML | 4.717 | 1.041 | 4.531 |
| evaluation_2000_2025 | Mom | 3.879 | 0.967 | 4.01 |


The historical reference gives momentum a HAC t-statistic of 4.43, so this study
cannot support a claim that momentum never earned a premium. The later 2020-2025
slice already has a weak naive momentum t-statistic. Period choice matters.


## All disjoint-window offsets

| factor | n_min | n_max | t_min | t_median | t_max |
| --- | --- | --- | --- | --- | --- |
| HML | 310 | 311 | 0.97 | 1.034 | 1.084 |
| Mkt-RF | 310 | 311 | 2.268 | 2.42 | 2.647 |
| Mom | 310 | 311 | 0.716 | 0.859 | 0.992 |
| SMB | 310 | 311 | 0.388 | 0.49 | 0.536 |


Every possible offset is retained. These t-statistics assume independence between
non-overlapping windows; no shared daily returns does not guarantee no dependence.


## Resampling sensitivity

| factor | block | draws | bootstrap_se | percentile_025 | percentile_975 |
| --- | --- | --- | --- | --- | --- |
| Mkt-RF | 21 | 2000 | 0.002839 | 0.000778 | 0.012085 |
| SMB | 21 | 2000 | 0.001704 | -0.002488 | 0.004211 |
| HML | 21 | 2000 | 0.00208 | -0.001801 | 0.006249 |
| Mom | 21 | 2000 | 0.003002 | -0.00364 | 0.00812 |
| Mkt-RF | 63 | 2000 | 0.002598 | 0.001731 | 0.011616 |
| SMB | 63 | 2000 | 0.001663 | -0.002471 | 0.00407 |
| HML | 63 | 2000 | 0.002179 | -0.002219 | 0.006452 |
| Mom | 63 | 2000 | 0.002758 | -0.003108 | 0.0076 |
| Mkt-RF | 126 | 2000 | 0.002693 | 0.001472 | 0.01173 |
| SMB | 126 | 2000 | 0.001466 | -0.001875 | 0.003864 |
| HML | 126 | 2000 | 0.002281 | -0.002444 | 0.006681 |
| Mom | 126 | 2000 | 0.002788 | -0.003404 | 0.007612 |


Circular moving-block bootstrap resamples real daily rows jointly across factors,
then re-forms 21-session windows, with 2,000 draws per block length. Percentile
intervals are resampling results, not observations or exact coverage guarantees.
All tested block lengths include zero for SMB, HML and Mom and exclude zero for
market excess. Bootstrap validity assumes sufficient stability of dependence.


## Interpretation and limits

Adjacent windows share 20 of 21 daily returns by construction. This design
demonstrates precision inflation in an unconditional arithmetic-mean test.
It does not estimate predictive alpha, transaction costs, trading capacity or
implementable net performance. Current-vintage factor definitions and historical
revisions limit real-time interpretation. Summed P&L uses constant daily notional;
it is not compounded factor wealth. Do not apply these numerical multipliers
automatically to predictive regressions: residual dependence can differ.
HAC and bootstrap inference remain approximate under heteroskedasticity,
nonstationarity and fat tails. The sqrt(h) line is an iid limiting reference;
the finite-bandwidth Bartlett estimator need not equal it even under iid daily
returns. No claim about false-positive rates is estimated here.


## Verification

See [verification.json](verification.json). Every primary 21-session P&L was
independently reconstructed from the saved daily CSV. A separate covariance
quadratic form and statsmodels OLS HAC agree with all headline statistics.
Saved bootstrap draws and non-overlap offsets were also checked.
