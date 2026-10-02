"""Deterministic answers for historical match results."""

from dataclasses import dataclass
from pathlib import Path
from re import fullmatch
from typing import Literal

from footballml.lookup import (
    MatchRecord,
    TeamCandidate,
    find_matches,
    find_teams,
    get_match,
)


@dataclass(frozen=True, slots=True)
class ResultAnswer:
    status: Literal["result", "clarify_team", "clarify_match", "not_found"]
    text: str
    team_options: tuple[tuple[int, ...], tuple[int, ...]] = ((), ())
    match_options: tuple[int, ...] = ()


def _fixture(match: MatchRecord) -> str:
    league = match.league_name or f"League ID {match.league_id}"
    home = match.home_team_name or f"Team ID {match.home_team_id}"
    away = match.away_team_name or f"Team ID {match.away_team_id}"
    return (
        f"{match.match_date.isoformat()} | {league} | {match.season} | "
        f"{home} vs {away} | match ID {match.match_id}"
    )


def _result(match: MatchRecord) -> ResultAnswer:
    return ResultAnswer(
        "result", f"{_fixture(match)} | result {match.home_goals}–{match.away_goals}"
    )


def answer_match(database_path: Path, match_id: int) -> ResultAnswer:
    """Answer from one exact match ID."""
    match = get_match(database_path, match_id)
    if match is None:
        return ResultAnswer("not_found", "No match with that ID exists in the dataset.")
    return _result(match)


def answer_team_ids(
    database_path: Path,
    first_team_id: int,
    second_team_id: int,
    *,
    season: str | None = None,
    league_id: int | None = None,
) -> ResultAnswer:
    """Return a unique result or list fixtures that need a match ID."""
    matches = find_matches(
        database_path,
        first_team_id,
        second_team_id,
        season=season,
        league_id=league_id,
    )
    if not matches:
        return ResultAnswer("not_found", "No match between those team IDs was found.")
    if len(matches) == 1:
        return _result(matches[0])
    return ResultAnswer(
        "clarify_match",
        "Which match do you mean?\n"
        + "\n".join(f"- {_fixture(match)}" for match in matches),
        match_options=tuple(match.match_id for match in matches),
    )


def _describe(candidates: list[TeamCandidate]) -> str:
    return "; ".join(
        f"{team.long_name} (team ID {team.team_id}, "
        f"seasons {', '.join(team.seasons) or 'none'})"
        for team in candidates
    )


def answer_teams(
    database_path: Path,
    first_name: str,
    second_name: str,
    *,
    season: str | None = None,
    league_id: int | None = None,
) -> ResultAnswer:
    """Resolve exact names without merging different team IDs."""
    if season is not None and (
        not isinstance(season, str) or fullmatch(r"[0-9]{4}/[0-9]{4}", season) is None
    ):
        raise ValueError("Season must have format YYYY/YYYY")
    if league_id is not None and (type(league_id) is not int or league_id <= 0):
        raise ValueError("League ID must be a positive integer")

    first = find_teams(database_path, first_name)
    second = find_teams(database_path, second_name)
    if not first or not second:
        return ResultAnswer("not_found", "One or both team names were not found.")

    if season is not None:
        first = [team for team in first if season in team.seasons]
        second = [team for team in second if season in team.seasons]
    if not first or not second:
        return ResultAnswer(
            "not_found", "One or both teams have no recorded matches in that season."
        )
    if len(first) != 1 or len(second) != 1:
        return ResultAnswer(
            "clarify_team",
            "Which team IDs do you mean? "
            f"First: {_describe(first)}. Second: {_describe(second)}.",
            team_options=(
                tuple(team.team_id for team in first),
                tuple(team.team_id for team in second),
            ),
        )
    return answer_team_ids(
        database_path,
        first[0].team_id,
        second[0].team_id,
        season=season,
        league_id=league_id,
    )
