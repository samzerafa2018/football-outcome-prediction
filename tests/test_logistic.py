from dataclasses import replace
from datetime import date

import pytest

from footballml.data import Outcome
from footballml.dataset import Example, ModelInputs
from footballml.logistic import fit_model, predict_probabilities


def _example(
    match_id: int, home_team_id: int, away_team_id: int, target: Outcome
) -> Example:
    return Example(
        match_id=match_id,
        match_date=date(2010, 8, 1),
        season="2010/2011",
        inputs=ModelInputs(1, home_team_id, away_team_id, 5, 5, 1.5, 1.0, 0.0, 0.0),
        target=target,
    )


def test_prediction_ignores_validation_result_and_handles_unseen_teams() -> None:
    labels: tuple[Outcome, ...] = ("H", "D", "A")
    train = [_example(i + 1, 10 + i % 3, 20 + i % 3, labels[i % 3]) for i in range(12)]
    model = fit_model(train)
    match = _example(50, 999, 998, "H")

    original = predict_probabilities(model, [match])[0]
    changed = predict_probabilities(
        model, [replace(match, match_date=date(2012, 8, 1), target="A")]
    )[0]

    assert original == changed
    assert set(original) == {"H", "D", "A"}
    assert sum(original.values()) == pytest.approx(1.0)
