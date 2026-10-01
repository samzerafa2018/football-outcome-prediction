from datetime import date
from math import log

import pytest

from footballml.baseline import evaluate_prior, fit_prior
from footballml.data import Outcome
from footballml.dataset import Example, ModelInputs


def example(match_id: int, target: Outcome) -> Example:
    return Example(
        match_id=match_id,
        match_date=date(2010, 8, 1),
        season="2010/2011",
        inputs=ModelInputs(1, 10, 20, 0, 0, 0.0, 0.0, 0.0, 0.0),
        target=target,
    )


def test_training_prior_and_validation_metrics() -> None:
    train = [
        example(1, "H"),
        example(2, "H"),
        example(3, "D"),
        example(4, "A"),
    ]
    validation = [example(5, "H"), example(6, "A")]

    probabilities = fit_prior(train)
    assert probabilities == {"H": 0.5, "D": 0.25, "A": 0.25}

    accuracy, log_loss, brier = evaluate_prior(validation, probabilities)
    assert accuracy == 0.5
    assert log_loss == pytest.approx((log(2) + log(4)) / 2)
    assert brier == pytest.approx(0.625)
