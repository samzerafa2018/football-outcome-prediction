from dataclasses import dataclass
from datetime import date

from footballml.data import Match, Outcome, outcome_for
from footballml.features import build_form_features


@dataclass(frozen=True, slots=True)
class ModelInputs:
    league_id: int
    home_team_id: int
    away_team_id: int
    home_matches: int
    away_matches: int
    home_points_per_match: float
    away_points_per_match: float


@dataclass(frozen=True, slots=True)
class Example:
    match_id: int
    match_date: date
    season: str
    inputs: ModelInputs
    target: Outcome


def build_examples(matches: list[Match], window: int = 5) -> list[Example]:
    """Build sequential pre-match examples from the complete match history."""
    ordered = sorted(matches, key=lambda m: (m.match_date, m.match_id))
    match_ids = {match.match_id for match in ordered}
    if len(match_ids) != len(ordered):
        raise ValueError("Duplicate match IDs")

    form_rows = build_form_features(ordered, window=window)
    form_by_id = {row.match_id: row for row in form_rows}
    if len(form_rows) != len(ordered) or set(form_by_id) != match_ids:
        raise ValueError("Form features do not match the matches")

    examples: list[Example] = []
    for match in ordered:
        form = form_by_id[match.match_id]
        examples.append(
            Example(
                match_id=match.match_id,
                match_date=match.match_date,
                season=match.season,
                inputs=ModelInputs(
                    league_id=match.league_id,
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    home_matches=form.home_matches,
                    away_matches=form.away_matches,
                    home_points_per_match=form.home_points_per_match,
                    away_points_per_match=form.away_points_per_match,
                ),
                target=outcome_for(match),
            )
        )
    return examples
