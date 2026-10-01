# Football Match Outcome Prediction

Predict pre-match probabilities for a home win, draw, or away win using historical European football results.

## Results

The selected model was evaluated on the held-out 2015/2016 season after model choices were fixed.

| Model | Accuracy | Log loss ↓ | Three-class Brier ↓ |
|---|---:|---:|---:|
| Training-prior baseline | 0.4387 | 1.0740 | 0.6498 |
| Logistic regression | **0.5024** | **1.0046** | **0.6006** |

Both models were fitted on the 22,653 matches from earlier seasons and evaluated on 3,326 test matches. The logistic model's equal-weight mean log loss across three earlier validation seasons was 0.9997. Validation guided model selection; the held-out season was used for final evaluation.

See [the logistic model report](reports/rolling_logistic.md) for the evaluated settings, rejected alternatives, calibration check, and final result. The [baseline report](reports/rolling_baseline.md) records the comparison across validation seasons.

### Historical bookmaker comparison

Valid Bet365 odds are available for 2,905 of the 3,326 test matches. On **those same 2,905 matches**, the normalized bookmaker odds score better than the selected model:

| Matched test subset | Accuracy | Log loss ↓ | Three-class Brier ↓ |
|---|---:|---:|---:|
| Training-prior baseline | 0.4434 | 1.0711 | 0.6479 |
| Logistic regression | 0.5105 | 0.9954 | 0.5942 |
| Bet365 normalized odds | **0.5201** | **0.9781** | **0.5829** |

This is a historical reference, not a model input or evidence of betting profitability. The database does not record when the odds were captured. See the [odds benchmark report](reports/odds_benchmark.md) for the method and limitations.

## Method

- **Data:** 25,979 matches across 11 European leagues, from 2008/2009 through 2015/2016.
- **Pre-match features:** league and team IDs, plus each team's match count, points per match, and goal difference per match over its latest 40 results.
- **Timing rule:** a match's features use results dated strictly before its calendar date. Recorded times do not establish the order of matches on the same day.
- **Model:** categorical encoding, feature scaling, and multiclass logistic regression with `C=0.03`. No probability temperature adjustment is applied.
- **Evaluation:** expanding-season validation on 2012/2013, 2013/2014, and 2014/2015, followed by the held-out 2015/2016 test. During evaluation, results from earlier dates in a season may inform later pre-match features; fitted model parameters and preprocessing stay fixed.

The [decisions log](docs/decisions.md) explains the timing and season-split rules. These results describe historical matches and do not establish performance on current matches.

## Setup and reproduction

The installable Python project uses isolated dependencies, Git version control, and automated code checks. It requires Python 3.13.

The raw *European Soccer Database* by Hugo Mathien is excluded from Git. Place its SQLite file at `Data/database.sqlite/database.sqlite`, then run these commands from the project root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m footballml.baseline
.\.venv\Scripts\python.exe -m footballml.evaluate_logistic
.\.venv\Scripts\python.exe -m footballml.evaluate_final
.\.venv\Scripts\python.exe -m footballml.evaluate_odds
```

The final four commands run the baseline validation, logistic validation, full held-out test, and matched-subset bookmaker benchmark, respectively.
