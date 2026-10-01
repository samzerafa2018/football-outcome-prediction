from collections.abc import Sequence
from math import isfinite

from sklearn.feature_extraction import DictVectorizer  # type: ignore[import-untyped]
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import MaxAbsScaler  # type: ignore[import-untyped]

from footballml.baseline import OUTCOMES
from footballml.data import Outcome
from footballml.dataset import Example


def _records(examples: Sequence[Example]) -> list[dict[str, str | int | float]]:
    """Read only the pre-match model inputs."""
    records: list[dict[str, str | int | float]] = []
    for row in examples:
        inputs = row.inputs
        records.append(
            {
                "league_id": str(inputs.league_id),
                "home_team_id": str(inputs.home_team_id),
                "away_team_id": str(inputs.away_team_id),
                "home_matches": inputs.home_matches,
                "away_matches": inputs.away_matches,
                "home_points_per_match": inputs.home_points_per_match,
                "away_points_per_match": inputs.away_points_per_match,
                "home_goal_difference_per_match": inputs.home_goal_difference_per_match,
                "away_goal_difference_per_match": inputs.away_goal_difference_per_match,
            }
        )
    return records


def fit_model(train: Sequence[Example], *, c: float = 0.03) -> Pipeline:
    """Fit the encoder, scaler, and classifier on training matches only."""
    if not train or {row.target for row in train} != set(OUTCOMES):
        raise ValueError("Training data must contain all three outcomes")
    if not isfinite(c) or c <= 0:
        raise ValueError("c must be finite and positive")

    model = Pipeline(
        [
            ("encoder", DictVectorizer(sparse=True)),
            ("scaler", MaxAbsScaler()),
            ("classifier", LogisticRegression(C=c, max_iter=1000)),
        ]
    )
    model.fit(_records(train), [row.target for row in train])
    return model


def predict_probabilities(
    model: Pipeline, examples: Sequence[Example]
) -> list[dict[Outcome, float]]:
    """Return probabilities labelled H, D, A."""
    if not examples:
        return []

    indices = {label: index for index, label in enumerate(model.classes_)}
    if set(indices) != set(OUTCOMES):
        raise ValueError("Model must predict all three outcomes")

    return [
        {outcome: float(probs[indices[outcome]]) for outcome in OUTCOMES}
        for probs in model.predict_proba(_records(examples))
    ]
