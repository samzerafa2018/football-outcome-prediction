# Logistic regression: rolling validation

## Method

Predict H/D/A probabilities from league ID, home and away team IDs, and each team's last-five-match count and points per match. Historical form uses results dated strictly before the match date.

Each fold trains a fresh regularized logistic regression model (`C=1.0`) on earlier seasons. Team and league IDs are encoded as categories; numeric form features are scaled. The encoder, scaler, and model are fitted only on that fold's training matches. During validation, earlier validation dates may inform later matches' form features, while the fitted model remains unchanged.

## Results

| Validation season | Matches | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|---:|
| 2012/2013 | 3,260 | 0.4810 | 1.0424 | 0.6239 |
| 2013/2014 | 3,032 | 0.4964 | 1.0142 | 0.6050 |
| 2014/2015 | 3,325 | 0.4968 | 1.0220 | 0.6094 |
| **Equal-weight fold mean** | | **0.4914** | **1.0262** | **0.6128** |

| Equal-weight mean | Training-prior baseline | Logistic regression |
|---|---:|---:|
| Accuracy | 0.4518 | **0.4914** |
| Log loss (lower is better) | 1.0676 | **1.0262** |
| Three-class Brier (lower is better) | 0.6452 | **0.6128** |

The logistic model improves log loss in every validation season. This is the first trained candidate with fixed settings, not the result of a hyperparameter search. The 2015/2016 final test season has not been evaluated.

## Reproduce

From the project root, run `.\.venv\Scripts\python.exe -m footballml.evaluate_logistic` with the database at `Data/database.sqlite/database.sqlite`.
