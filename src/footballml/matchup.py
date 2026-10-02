"""Exploratory matchup estimates from a model fitted on all recorded matches."""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]

from footballml.data import Outcome, load_matches
from footballml.dataset import Example, ModelInputs, build_examples
from footballml.logistic import fit_model, predict_probabilities
from footballml.predictions import FORM_WINDOW, MODEL_C, MODEL_VERSION

FULL_MODEL_VERSION = f"{MODEL_VERSION}-full"


@dataclass(frozen=True, slots=True)
class FullModel:
    pipeline: Pipeline
    form: dict[int, tuple[int, float, float]]
    trained_through: date
    training_matches: int


def fit_full_model(database_path: Path) -> FullModel:
    """Fit once on all recorded results; retain each team's latest form."""
    matches = load_matches(database_path)
    if not matches:
        raise ValueError("No recorded matches")
    model = fit_model(build_examples(matches, window=FORM_WINDOW), c=MODEL_C)
    recent: dict[int, deque[tuple[int, int]]] = defaultdict(
        lambda: deque(maxlen=FORM_WINDOW)
    )
    for match in matches:
        for team, goals_for, goals_against in (
            (match.home_team_id, match.home_goals, match.away_goals),
            (match.away_team_id, match.away_goals, match.home_goals),
        ):
            points = 3 if goals_for > goals_against else int(goals_for == goals_against)
            recent[team].append((points, goals_for - goals_against))
    form = {
        team: (
            len(results),
            sum(points for points, _ in results) / len(results),
            sum(difference for _, difference in results) / len(results),
        )
        for team, results in recent.items()
    }
    return FullModel(model, form, matches[-1].match_date, len(matches))


def predict_matchup(
    fitted: FullModel, league_id: int, home_team_id: int, away_team_id: int
) -> dict[Outcome, float]:
    """Estimate a hypothetical next match using form through the data cutoff."""
    if home_team_id == away_team_id:
        raise ValueError("Choose two different teams")
    if home_team_id not in fitted.form or away_team_id not in fitted.form:
        raise ValueError("Both teams need recorded results")
    h_count, h_points, h_difference = fitted.form[home_team_id]
    a_count, a_points, a_difference = fitted.form[away_team_id]
    inputs = ModelInputs(
        league_id,
        home_team_id,
        away_team_id,
        h_count,
        a_count,
        h_points,
        a_points,
        h_difference,
        a_difference,
    )
    # The label is never used for prediction; only Example.inputs enter the pipeline.
    example = Example(
        0, fitted.trained_through + timedelta(days=1), "hypothetical", inputs, "D"
    )
    return predict_probabilities(fitted.pipeline, [example])[0]
