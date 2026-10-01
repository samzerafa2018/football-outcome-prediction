# Logistic regression: rolling validation

## Protocol

Predict pre-match H/D/A probabilities across three expanding-season folds, validating on 2012/2013, 2013/2014, and 2014/2015. For a match on date D, form uses results dated strictly before D. Earlier validation results may inform features for later validation dates; the fitted model stays fixed within each fold.

Each fold fits a new `DictVectorizer`, `MaxAbsScaler`, and regularized logistic regression on earlier seasons only. League and team IDs are categorical. Match counts, points per match, and (in the current model) goal difference per match are numeric.

## Points-only model selection

The selection criterion was equal-weight mean validation log loss. We compared `C` values with a five-match form window, compared windows at `C=0.1`, then checked nearby combinations. Every row below used **points and match counts without goal difference**.

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

Window 40 and `C=0.03` had the lowest mean log loss among those points-only settings.

## Goal-difference feature comparison

We then added each team's prior 40-match goal difference per match, keeping window 40, `C=0.03`, and all validation folds fixed. This isolates the effect of the new features.

| Validation season | Points only log loss | With goal difference log loss |
|---|---:|---:|
| 2012/2013 | 1.0163 | **1.0118** |
| 2013/2014 | 0.9934 | **0.9892** |
| 2014/2015 | 1.0024 | **0.9982** |
| **Equal-weight fold mean** | **1.0040** | **0.9997** |

Goal difference improves log loss in all three folds. The gain is modest, so this is evidence for keeping the feature, not a claim that its effect is precisely known.

## Current model results

| Validation season | Matches | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|---:|
| 2012/2013 | 3,260 | 0.4997 | 1.0118 | 0.6053 |
| 2013/2014 | 3,032 | 0.5234 | 0.9892 | 0.5895 |
| 2014/2015 | 3,325 | 0.5146 | 0.9982 | 0.5959 |
| **Equal-weight fold mean** | | **0.5126** | **0.9997** | **0.5969** |

| Equal-weight mean | Training-prior baseline | Points-only model | Current model |
|---|---:|---:|---:|
| Accuracy | 0.4518 | 0.5091 | **0.5126** |
| Log loss | 1.0676 | 1.0040 | **0.9997** |
| Three-class Brier | 0.6452 | 0.5998 | **0.5969** |

These validation folds were used for model and feature selection, so their scores are not an independent final estimate. The 2015/2016 season remains reserved for final testing.
## Calibration check

Across the three validation seasons, average predicted outcome rates were close to observed rates. Five equal-sized probability groups per outcome showed some underconfidence for high home- and away-win probabilities.

| Temperature | 2012/2013 | 2013/2014 | 2014/2015 | Mean log loss |
|---:|---:|---:|---:|---:|
| 0.8 | 1.0164 | 0.9882 | 1.0010 | 1.0018 |
| 0.9 | 1.0127 | 0.9876 | 0.9982 | 0.9995 |
| **1.0 (unchanged)** | **1.0118** | **0.9892** | **0.9982** | **0.9997** |
| 1.1 | 1.0125 | 0.9920 | 0.9997 | 1.0014 |

The 0.0002 mean improvement at temperature 0.9 is negligible and does not hold in every season. Keep the unadjusted probabilities. These are model-selection results; the 2015/2016 test season was not used.

## Final held-out evaluation

After selecting the features and settings using validation seasons, refit on all seven earlier seasons (22,653 matches) and evaluate on 2015/2016 (3,326 matches). The selected model uses a 40-match form window, points and goal difference, `C=0.03`, and no temperature adjustment.

| Model | Accuracy | Log loss | Three-class Brier |
|---|---:|---:|---:|
| Training-prior baseline | 0.4387 | 1.0740 | 0.6498 |
| Selected logistic model | **0.5024** | **1.0046** | **0.6006** |

The logistic model improves accuracy by 6.37 percentage points and reduces log loss by 0.0694. Both models were fitted using only pre-test seasons. For sequential predictions, results from earlier test dates may inform later pre-match form features; test labels are never used to fit the model or preprocessing. No model setting was changed after seeing this test result.

## Reproduce

With the database at `Data/database.sqlite/database.sqlite`, run `.\.venv\Scripts\python.exe -m footballml.evaluate_logistic` from the project root for the current model's scores. The points-only version and its report are preserved in Git history.
For the held-out result, run `.\.venv\Scripts\python.exe -m footballml.evaluate_final`.
