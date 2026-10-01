# Decisions log

## 2026-09-30 — Treat match timestamps as calendar dates

**Evidence:** All 25,979 `Match.date` values have the time `00:00:00`.

**Decision:** For a match on date D, historical features may use results only from dates earlier than D. Match IDs and row order do not establish kick-off order.

**Reason:** The recorded time cannot tell us which same-day match finished first. Using a same-day result could leak information unavailable before kick-off.

**Tradeoff:** We may omit a legitimately earlier same-day result.

**Verification:** Test that a match's features exclude its own result, all later results, and every result dated the same day.

## 2026-09-30 - Split by season

**Evidence:** The database contains eight consecutive seasons from 2008/2009 to 2015/2016, with 3,032 to 3,326 matches per season.

**Decision:** Train on 2008/2009 through 2013/2014 (19,328 matches), validate on 2014/2015 (3,325), and use 2015/2016 as the final test (3,326). Do not shuffle matches across these periods.

**Reason:** Validation and testing should measure predictions for seasons later than the training data. Choose features and model settings using validation; reserve the test season for the final evaluation.

**Feature timing:** For a match on date D, use results dated strictly before D, including previously observed results during validation or test when making sequential pre-match predictions. Fit learned preprocessing only on training data.

## 2026-10-01 - Use expanding-season validation

**Decision:** Compare model choices across validation seasons 2012/2013, 2013/2014, and 2014/2015. For each fold, train on all available earlier seasons. Use the equal-weight mean validation log loss for model selection and report each season separately.

**Relation to the earlier split:** The 2014/2015 validation season is now the third fold. The 2015/2016 season remains the final test and is excluded from model selection.

**Reason:** Results from one season may be unusually favourable or difficult. Expanding folds show whether a model's probabilistic performance is reasonably stable over time.

**Forecast timing:** Features for date D use results strictly before D. Fit model parameters and learned preprocessing separately within each fold's training data.
