from collections.abc import Mapping, Sequence
from math import log
from pathlib import Path
from random import Random

from footballml.baseline import fit_prior
from footballml.data import (
    TEST_SEASON,
    TRAIN_SEASONS,
    VALIDATION_SEASON,
    Outcome,
    load_matches,
)
from footballml.dataset import Example, build_examples
from footballml.evaluate_odds import _load_bet365
from footballml.logistic import fit_model, predict_probabilities

DATABASE = Path("Data/database.sqlite/database.sqlite")


def paired_log_loss_gain(
    rows: Sequence[Example],
    candidate: Mapping[int, Mapping[Outcome, float]],
    reference: Mapping[int, Mapping[Outcome, float]],
) -> tuple[float, float, float]:
    """Positive values mean the candidate has lower log loss."""
    ids = {row.match_id for row in rows}
    if (
        not rows
        or len(ids) != len(rows)
        or set(candidate) != ids
        or set(reference) != ids
    ):
        raise ValueError("Predictions must match unique example IDs")

    weeks: dict[tuple[int, int], tuple[float, int]] = {}
    for row in rows:
        day = row.match_date.isocalendar()
        key = (day.year, day.week)
        gain = log(candidate[row.match_id][row.target]) - log(
            reference[row.match_id][row.target]
        )
        total, count = weeks.get(key, (0.0, 0))
        weeks[key] = total + gain, count + 1

    groups = list(weeks.values())
    if len(groups) < 2:
        raise ValueError("At least two calendar weeks are required")

    estimate = sum(total for total, _ in groups) / len(rows)
    rng = Random(2026)
    samples = []
    for _ in range(2_000):
        selected = rng.choices(groups, k=len(groups))
        samples.append(
            sum(total for total, _ in selected) / sum(count for _, count in selected)
        )
    samples.sort()
    return estimate, samples[50], samples[1_950]


def main() -> None:
    examples = build_examples(load_matches(DATABASE))
    train = [
        row
        for row in examples
        if row.season in TRAIN_SEASONS or row.season == VALIDATION_SEASON
    ]
    test = [row for row in examples if row.season == TEST_SEASON]

    prior = fit_prior(train)
    model = fit_model(train)
    model_probs = dict(
        zip(
            (row.match_id for row in test),
            predict_probabilities(model, test),
            strict=True,
        )
    )
    baseline_probs = {row.match_id: prior for row in test}

    gain, low, high = paired_log_loss_gain(test, model_probs, baseline_probs)
    print(
        f"Logistic over baseline, {len(test)} matches: "
        f"gain={gain:.4f}, 95% interval=[{low:.4f}, {high:.4f}]"
    )

    odds = _load_bet365(DATABASE)
    matched = [row for row in test if row.match_id in odds]
    matched_model = {row.match_id: model_probs[row.match_id] for row in matched}
    matched_odds = {row.match_id: odds[row.match_id] for row in matched}
    gain, low, high = paired_log_loss_gain(matched, matched_odds, matched_model)
    print(
        f"Bet365 over logistic, {len(matched)} matched matches: "
        f"gain={gain:.4f}, 95% interval=[{low:.4f}, {high:.4f}]"
    )


if __name__ == "__main__":
    main()
