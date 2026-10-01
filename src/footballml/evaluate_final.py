from pathlib import Path

from footballml.baseline import evaluate_prior, fit_prior
from footballml.data import TEST_SEASON, TRAIN_SEASONS, VALIDATION_SEASON, load_matches
from footballml.dataset import build_examples
from footballml.evaluate_logistic import score_predictions
from footballml.logistic import fit_model, predict_probabilities


def main() -> None:
    examples = build_examples(
        load_matches(Path("Data/database.sqlite/database.sqlite"))
    )
    train = [
        row
        for row in examples
        if row.season in TRAIN_SEASONS or row.season == VALIDATION_SEASON
    ]
    test = [row for row in examples if row.season == TEST_SEASON]

    if not train or not test or len(train) + len(test) != len(examples):
        raise ValueError("Unexpected season split")
    if max(row.match_date for row in train) >= min(row.match_date for row in test):
        raise ValueError("Training must precede testing")

    baseline = evaluate_prior(test, fit_prior(train))
    model = fit_model(train)
    logistic = score_predictions(test, predict_probabilities(model, test))

    print(f"Training matches: {len(train)}; test matches: {len(test)}")
    for name, (accuracy, log_loss, brier) in (
        ("Training-prior baseline", baseline),
        ("Selected logistic model", logistic),
    ):
        print(
            f"{name}: accuracy={accuracy:.4f}, "
            f"log_loss={log_loss:.4f}, brier={brier:.4f}"
        )


if __name__ == "__main__":
    main()
