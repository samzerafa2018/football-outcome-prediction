# Historical bookmaker-odds benchmark

## Method

Compare the training-prior baseline, selected logistic model, and Bet365 odds on the same 2015/2016 matches. Fit both models on all seven earlier seasons (22,653 matches). Keep the logistic model's selected settings fixed.

The source is the *European Soccer Database* by Hugo Mathien, which attributes betting odds to Football-Data.co.uk. Use `B365H`, `B365D`, and `B365A` only when all three decimal odds exceed 1 and are finite. Convert each odd to its reciprocal and divide each reciprocal by the sum of all three. This proportionally normalizes the bookmaker overround so H/D/A probabilities sum to 1.

Valid Bet365 triplets exist for 2,905 of 3,326 test matches (87.3%). Score every method on those same 2,905 matches. The full-test model result remains separately reported in `rolling_logistic.md`.

## Matched-subset results

| Method | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|
| Training-prior baseline | 0.4434 | 1.0711 | 0.6479 |
| Selected logistic model | 0.5105 | 0.9954 | 0.5942 |
| Bet365 normalized odds | **0.5201** | **0.9781** | **0.5829** |

Bet365 has 0.0173 lower log loss than the logistic model on this subset. This is a descriptive historical comparison, not a model-selection result or evidence of betting profitability. The database does not record when these odds were captured, and the 421 matches without valid Bet365 triplets are excluded.

## Reproduce

From the project root, with the SQLite data at `Data/database.sqlite/database.sqlite`:

```powershell
.\.venv\Scripts\python.exe -m footballml.evaluate_odds
```
