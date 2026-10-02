# Evaluation record

This is a retrospective record written after the 2015/2016 test results were viewed. It is not a preregistration.

## Selection and first test

Model choices used expanding-season validation on 2012/2013, 2013/2014, and 2014/2015. The primary selection criterion was equal-weight mean validation log loss. The selected model uses a 40-match form window, points and goal difference, logistic regression with `C=0.03`, and no probability temperature adjustment.

The selected model was committed at `12ae983c94b3be4c19a996b155fddf5d999a70ea`. Its 2015/2016 held-out results were subsequently recorded at `978cd69f7c36665762f082bcb78a0af71aa6bc17`: log loss 1.0046 versus 1.0740 for the training-prior baseline, on 3,326 matches. Accuracy and three-class Brier are secondary metrics.

After that result was viewed, a Bet365 comparison was added at `a565ce766ce707c25d5f088b6e7b1fa96a0d3751`. It compares the same models on the 2,905 test matches with complete odds. This is a subsequent benchmark, not a new independent test or a basis for changing the selected model.

The 2015/2016 results describe the evaluated, already-selected model. Any future model chosen using knowledge of those results requires new data for a fresh independent evaluation.

## Reproduction and limits

Audited database SHA-256: `4DF8569777D59FDD690754B1CC8CA1F7989BAF65F2EADDD0F1368285F11139A9`.

The database coverage and competition-phase limits are documented in `docs/data_card.md`. The current repository commit at the time of this audit was `fac6686bcc9e3537c5b1a343a0276361d6e6870d`. This commit is later than the first test run; use the earlier model commit above when identifying the original evaluation code.
