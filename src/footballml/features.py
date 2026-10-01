from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import groupby

from footballml.data import Match

DEFAULT_FORM_WINDOW = 40


@dataclass(frozen=True, slots=True)
class FormFeatures:
    match_id: int
    home_matches: int
    away_matches: int
    home_points_per_match: float
    away_points_per_match: float


def _points(goals_for: int, goals_against: int) -> int:
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def _average(points: deque[int]) -> float:
    return sum(points) / len(points) if points else 0.0


def build_form_features(
    matches: list[Match], window: int = DEFAULT_FORM_WINDOW
) -> list[FormFeatures]:
    """Use only results from dates strictly before each match."""
    if window < 1:
        raise ValueError("window must be at least 1")

    history: defaultdict[int, deque[int]] = defaultdict(
        lambda: deque[int](maxlen=window)
    )
    features: list[FormFeatures] = []

    ordered = sorted(matches, key=lambda match: (match.match_date, match.match_id))
    for _, daily_matches in groupby(ordered, key=lambda match: match.match_date):
        day = list(daily_matches)

        # Snapshot all features before adding any results from this date.
        for match in day:
            home = history[match.home_team_id]
            away = history[match.away_team_id]
            features.append(
                FormFeatures(
                    match_id=match.match_id,
                    home_matches=len(home),
                    away_matches=len(away),
                    home_points_per_match=_average(home),
                    away_points_per_match=_average(away),
                )
            )

        for match in day:
            history[match.home_team_id].append(
                _points(match.home_goals, match.away_goals)
            )
            history[match.away_team_id].append(
                _points(match.away_goals, match.home_goals)
            )

    return features
