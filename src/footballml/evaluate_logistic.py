from collections.abc import Sequence
from math import log
from pathlib import Path

from footballml.baseline import OUTCOMES
from footballml.data import Outcome, load_matches
from footballml.dataset import Example, build_examples
from footballml.logistic import fit_model, predict_probabilities
from footballml.validation import rolling_validation_folds


def score_predictions(
    examples: Sequence[Example],
    predictions: Sequence[dict[Outcome, float]],
) -> tuple[float, float, float]:
    """Return accuracy, log loss, and three-class Brier score."""
    if not examples or len(examples) != len(predictions):
        raise ValueError("Examples and predictions must have equal nonzero lengths")

    accuracy = sum(
        max(OUTCOMES, key=lambda outcome: probs[outcome]) == row.target
        for row, probs in zip(examples, predictions, strict=True)
    ) / len(examples)
    log_loss = -sum(
        log(probs[row.target]) for row, probs in zip(examples, predictions, strict=True)
    ) / len(examples)
    brier = sum(
        sum(
            (probs[outcome] - float(row.target == outcome)) ** 2 for outcome in OUTCOMES
        )
        for row, probs in zip(examples, predictions, strict=True)
    ) / len(examples)
    return accuracy, log_loss, brier


def main() -> None:
    matches = load_matches(Path("Data/database.sqlite/database.sqlite"))
    folds = rolling_validation_folds(build_examples(matches))
    results: list[tuple[float, float, float]] = []

    for fold in folds:
        model = fit_model(fold.train)
        predictions = predict_probabilities(model, fold.validation)
        accuracy, log_loss, brier = score_predictions(fold.validation, predictions)
        results.append((accuracy, log_loss, brier))
        print(
            f"{fold.validation_season}: "
            f"accuracy={accuracy:.4f}, "
            f"log_loss={log_loss:.4f}, "
            f"brier={brier:.4f}"
        )

    count = len(results)
    print(f"Mean validation accuracy: {sum(r[0] for r in results) / count:.4f}")
    print(f"Mean validation log loss: {sum(r[1] for r in results) / count:.4f}")
    print(f"Mean validation Brier score: {sum(r[2] for r in results) / count:.4f}")


if __name__ == "__main__":
    main()
