# Logistic regression: rolling validation

## Method

Predict H/D/A probabilities from league ID, home and away team IDs, and each team's last-five-match count and points per match. Historical form uses results dated strictly before the match date.

Each fold fits a fresh pipeline on earlier seasons: categorical IDs are encoded with `DictVectorizer`, features are scaled with `MaxAbsScaler`, and a regularized logistic regression predicts the outcome. During validation, earlier validation dates may inform later matches' form features; the fitted pipeline does not change during that validation season.

## Regularization selection

Compare `C` values using the equal-weight mean log loss across the three validation seasons. Lower `C` means stronger regularization; lower log loss is better.

| C | 2012/2013 | 2013/2014 | 2014/2015 | Mean log loss |
|---:|---:|---:|---:|---:|
| 0.01 | 1.0379 | 1.0188 | 1.0262 | 1.0276 |
| 0.03 | 1.0290 | 1.0076 | 1.0146 | 1.0171 |
| **0.1** | **1.0267** | **1.0028** | **1.0095** | **1.0130** |
| 1.0 | 1.0424 | 1.0142 | 1.0220 | 1.0262 |
| 10.0 | 1.0497 | 1.0205 | 1.0308 | 1.0337 |

`C=0.1` has the lowest log loss in each fold and is the selected setting.

## Selected model results

| Validation season | Matches | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|---:|
| 2012/2013 | 3,260 | 0.4859 | 1.0267 | 0.6151 |
| 2013/2014 | 3,032 | 0.5056 | 1.0028 | 0.5985 |
| 2014/2015 | 3,325 | 0.5023 | 1.0095 | 0.6031 |
| **Equal-weight fold mean** | | **0.4979** | **1.0130** | **0.6056** |

| Equal-weight mean | Training-prior baseline | Selected logistic model |
|---|---:|---:|
| Accuracy | 0.4518 | **0.4979** |
| Log loss | 1.0676 | **1.0130** |
| Three-class Brier | 0.6452 | **0.6056** |

The selected model improves log loss in all three validation seasons. Because these folds were used to choose `C`, their scores are model-selection results. The 2015/2016 season remains reserved for the final independent evaluation.

## Reproduce

From the project root, with the database at `Data/database.sqlite/database.sqlite`, run `.\.venv\Scripts\python.exe -m footballml.evaluate_logistic` to reproduce the selected model's scores.
