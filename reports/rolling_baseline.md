# Training-prior baseline

## Evaluation protocol

Predict home win, draw, or away win before each match date. Pre-match form uses results from strictly earlier calendar dates. During validation, results from earlier validation dates may inform later matches; this represents daily sequential forecasting.

Each fold estimates one constant set of H/D/A probabilities from its training seasons. It does not use match features. The 2015/2016 season remains reserved for final testing.

| Training matches | Validation season | Validation matches | Accuracy | Log loss | Three-class Brier |
|---:|---|---:|---:|---:|---:|
| 13,036 | 2012/2013 | 3,260 | 0.4429 | 1.0732 | 0.6492 |
| 16,296 | 2013/2014 | 3,032 | 0.4631 | 1.0607 | 0.6404 |
| 19,328 | 2014/2015 | 3,325 | 0.4493 | 1.0688 | 0.6461 |
| | **Equal-weight fold mean** | | **0.4518** | **1.0676** | **0.6452** |

Lower log loss and Brier scores are better. The three-class Brier score is the mean, over matches, of the sum of squared probability errors across H, D, and A. Uniform probabilities would score approximately 1.0986 log loss and 0.6667 Brier.

## Reproduce

From the project root, with the database at `Data/database.sqlite/database.sqlite`:

```powershell
.\.venv\Scripts\python.exe -m footballml.baseline
```
Model choices will be compared across these validation folds. The 2015/2016 test season is not used for model selection.
