# Football Match Outcome Prediction

Predict pre-match probabilities for a home win, draw, or away win using historical European football results.

## Results

The selected model was evaluated retrospectively on the 2015/2016 season. Because test results were inspected during development, these scores are not a fresh independent estimate of future performance.

| Model | Accuracy | Log loss ↓ | Three-class Brier ↓ |
|---|---:|---:|---:|
| Training-prior baseline | 0.4387 | 1.0740 | 0.6498 |
| Logistic regression | **0.5024** | **1.0046** | **0.6006** |

Both models were fitted on the 22,653 matches from earlier seasons and evaluated on 3,326 test matches. The logistic model's equal-weight mean log loss across three earlier validation seasons was 0.9997. Validation guided model selection; the held-out season was used for final evaluation.

See [the logistic model report](reports/rolling_logistic.md) for the evaluated settings, rejected alternatives, calibration check, and final result. The [baseline report](reports/rolling_baseline.md) records the comparison across validation seasons.

The [uncertainty report](reports/uncertainty.md) gives paired intervals for the held-out log-loss comparisons.

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

## Explore historical matches

The command-line interface uses exact team names and match IDs. It retrieves recorded scores and can show stored pre-match probabilities for 2015/2016 fixtures.

```powershell
.\.venv\Scripts\python.exe -m footballml.query teams "BSC Young Boys" "FC Basel" --season "2008/2009"
.\.venv\Scripts\python.exe -m footballml.query build-forecasts
.\.venv\Scripts\python.exe -m footballml.query forecast-teams "BSC Young Boys" "FC Basel"
.\.venv\Scripts\python.exe -m footballml.query forecast 25979
.\.venv\Scripts\python.exe -m footballml.query league-performance
```

`build-forecasts` fits the selected logistic model on seasons through 2014/2015 and saves 3,326 held-out predictions under `Data/`, which is excluded from Git. If two teams met more than once, select a match ID before viewing its forecast. These are historical 2015/2016 predictions, not forecasts for current matches.

`league-performance` ranks leagues by the mean points per recorded match of their top quarter of teams, rounded up. In 2015/2016 Portugal ranks first on this measure at 2.112. This measures domestic points concentration; it cannot establish which league has the strongest teams.

## Local app

The light-themed Streamlit app lets you retrieve recorded results from any season, compare the historical performance of leagues, and view the saved 2015/2016 pre-match forecasts. Its **Predict a matchup** page fits the selected model once on all 25,979 matches, then estimates a hypothetical next match using each team's latest recorded form and an assumed league. The fitted model is cached while the app runs. Those exploratory estimates use information through 2016 and are not live forecasts or an independent test result.

The prediction views show all three outcome probabilities on a 0–100% chart. The league view charts the top-quarter points-per-match measure and keeps exact figures in an expandable table.

**Reading a prediction:** The 50.24% accuracy in the Results table belongs to the model trained through 2014/2015 and tested on 2015/2016. It is not a measured accuracy for the app's full-data matchup predictor; this database has no later season on which to test that version. A 47% win probability means a 47% estimated chance of that outcome, not 47% model accuracy. A draw and the other team's win may together be more likely. For teams absent from the final recorded season, their latest form is older still, and the league selected in the app is an assumption.

From the project root in PowerShell, install the optional UI dependency and create the historical forecast archive once:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ui]"
.\.venv\Scripts\python.exe -m footballml.query build-forecasts
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local address printed by Streamlit. The SQLite database and generated forecast archive stay under `Data/` and are excluded from Git.

## Future designs

- **Refresh the data:** Add post-2016 results and verified pre-match information to support more relevant forecasts.
- **Improve predictive accuracy:** Test stronger team-form and rating features against the current model, while tracking log loss and probability calibration as well as accuracy.
- **Evaluate and explain:** Test on a new, unseen season and add team-form trends and clearer prediction explanations to the app.
