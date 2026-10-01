from collections import Counter
from collections.abc import Mapping, Sequence
from math import log
from pathlib import Path

from footballml.data import (
    TRAIN_SEASONS,
    VALIDATION_SEASON,
    Outcome,
    load_matches,
)
from footballml.dataset import Example, build_examples

OUTCOMES: tuple[Outcome, Outcome, Outcome] = ("H", "D", "A")


def fit_prior(train: Sequence[Example]) -> dict[Outcome, float]:
    """Estimate constant outcome probabilities using training labels only."""
    if not train:
        raise ValueError("Training examples cannot be empty")

    counts: Counter[Outcome] = Counter(row.target for row in train)
    if any(counts[outcome] == 0 for outcome in OUTCOMES):
        raise ValueError("Training data must contain all three outcomes")

    return {outcome: counts[outcome] / len(train) for outcome in OUTCOMES}


def evaluate_prior(
    validation: Sequence[Example],
    probabilities: Mapping[Outcome, float],
) -> tuple[float, float, float]:
    """Return accuracy, log loss, and three-class Brier score."""
    if not validation:
        raise ValueError("Validation examples cannot be empty")

    majority = max(OUTCOMES, key=lambda outcome: probabilities[outcome])
    accuracy = sum(row.target == majority for row in validation) / len(validation)
    log_loss = -sum(log(probabilities[row.target]) for row in validation) / len(
        validation
    )
    brier = sum(
        sum(
            (probabilities[outcome] - float(row.target == outcome)) ** 2
            for outcome in OUTCOMES
        )
        for row in validation
    ) / len(validation)
    return accuracy, log_loss, brier


def main() -> None:
    matches = load_matches(Path("Data/database.sqlite/database.sqlite"))
    examples = build_examples(matches)
    train = [row for row in examples if row.season in TRAIN_SEASONS]
    validation = [row for row in examples if row.season == VALIDATION_SEASON]

    probabilities = fit_prior(train)
    accuracy, log_loss, brier = evaluate_prior(validation, probabilities)
    print("Training probabilities H/D/A:", probabilities)
    print(f"Validation accuracy: {accuracy:.4f}")
    print(f"Validation log loss: {log_loss:.4f}")
    print(f"Validation three-class Brier score: {brier:.4f}")


if __name__ == "__main__":
    main()
