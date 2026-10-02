# Uncertainty in held-out log-loss comparisons

The selected logistic model and training-prior baseline were compared on the same 3,326 matches in 2015/2016. Bet365 normalized odds and the logistic model were compared on the same 2,905 matches with complete odds. Positive gains mean lower log loss for the first model named.

| Paired comparison | Matches | Mean log-loss gain | 95% bootstrap interval |
|---|---:|---:|---:|
| Logistic over training prior | 3,326 | 0.0694 | [0.0582, 0.0807] |
| Bet365 normalized odds over logistic | 2,905 | 0.0173 | [0.0094, 0.0252] |

For each match, the gain is `log(P_first(actual outcome)) - log(P_second(actual outcome))`. Matches are grouped by ISO calendar week across leagues. The code resamples those weeks with replacement 2,000 times (seed `2026`) and uses the 2.5th and 97.5th percentiles of the resampled, match-weighted mean. Grouping preserves within-week variation during resampling; it does not account for every source of dependence or uncertainty from model selection.

These intervals describe this historical dataset and the already-selected model. The odds comparison applies only to matches with complete Bet365 odds; the database does not establish when the odds were captured. Neither comparison measures performance on current matches.

Reproduce from the project root with `Data/database.sqlite/database.sqlite` in place:

```powershell
.\.venv\Scripts\python.exe -m footballml.evaluate_uncertainty
```

Database SHA-256: `4DF8569777D59FDD690754B1CC8CA1F7989BAF65F2EADDD0F1368285F11139A9`.
