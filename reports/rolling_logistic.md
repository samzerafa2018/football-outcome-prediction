# Logistic regression: rolling validation

## Protocol

Predict pre-match H/D/A probabilities using league and team IDs, plus each team's match count and points per match over its most recent results. Results dated on or after a match's calendar date are excluded from its features.

Three expanding-season folds validate on 2012/2013, 2013/2014, and 2014/2015. Each fold fits a new `DictVectorizer`, `MaxAbsScaler`, and logistic regression using earlier seasons only. Earlier validation results may inform features for later dates in that season; the fitted pipeline stays fixed.

## Model selection

The selection criterion is equal-weight mean validation log loss. We first compared `C` values at window 5, compared windows at `C=0.1`, then checked nearby combinations for windows 20 and 40. This table records every combination evaluated, including rejected settings.

| Form window | C | 2012/2013 | 2013/2014 | 2014/2015 | Mean log loss |
|---:|---:|---:|---:|---:|---:|
| 3 | 0.1 | 1.0278 | 1.0046 | 1.0101 | 1.0142 |
| 5 | 0.01 | 1.0379 | 1.0188 | 1.0262 | 1.0276 |
| 5 | 0.03 | 1.0290 | 1.0076 | 1.0146 | 1.0171 |
| 5 | 0.1 | 1.0267 | 1.0028 | 1.0095 | 1.0130 |
| 5 | 1.0 | 1.0424 | 1.0142 | 1.0220 | 1.0262 |
| 5 | 10.0 | 1.0497 | 1.0205 | 1.0308 | 1.0337 |
| 10 | 0.1 | 1.0239 | 0.9981 | 1.0084 | 1.0101 |
| 20 | 0.01 | 1.0272 | 1.0045 | 1.0161 | 1.0159 |
| 20 | 0.03 | 1.0181 | 0.9948 | 1.0076 | 1.0068 |
| 20 | 0.1 | 1.0196 | 0.9949 | 1.0066 | 1.0071 |
| 40 | 0.01 | 1.0252 | 1.0034 | 1.0109 | 1.0132 |
| **40** | **0.03** | **1.0163** | **0.9934** | **1.0024** | **1.0040** |
| 40 | 0.1 | 1.0190 | 0.9946 | 1.0032 | 1.0056 |
| 80 | 0.1 | 1.0200 | 0.9998 | 1.0035 | 1.0078 |

Window 40 and `C=0.03` have the lowest mean log loss among the evaluated settings. The difference from nearby candidates is small; these validation results were used for selection and are not an independent final estimate.

## Selected model results

| Validation season | Matches | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|---:|
| 2012/2013 | 3,260 | 0.4948 | 1.0163 | 0.6084 |
| 2013/2014 | 3,032 | 0.5208 | 0.9934 | 0.5923 |
| 2014/2015 | 3,325 | 0.5119 | 1.0024 | 0.5987 |
| **Equal-weight fold mean** | | **0.5091** | **1.0040** | **0.5998** |

| Equal-weight mean | Training-prior baseline | Selected logistic model |
|---|---:|---:|
| Accuracy | 0.4518 | **0.5091** |
| Log loss | 1.0676 | **1.0040** |
| Three-class Brier | 0.6452 | **0.5998** |

The selected model improves log loss over the prior baseline in all three validation seasons. The 2015/2016 season remains reserved for the final independent evaluation.

## Reproduce

With the database at `Data/database.sqlite/database.sqlite`, run `.\.venv\Scripts\python.exe -m footballml.evaluate_logistic` from the project root for the selected model's scores.
