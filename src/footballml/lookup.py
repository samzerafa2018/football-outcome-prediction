import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from re import fullmatch


@dataclass(frozen=True, slots=True)
class TeamCandidate:
    team_id: int
    long_name: str
    short_name: str | None
    leagues: tuple[str, ...]
    seasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MatchRecord:
    match_id: int
    league_id: int
    league_name: str | None
    season: str
    match_date: date
    home_team_id: int
    home_team_name: str | None
    away_team_id: int
    away_team_name: str | None
    home_goals: int
    away_goals: int


_MATCH_SELECT = """
SELECT m.id, m.league_id, l.name, m.season, m.date,
       m.home_team_api_id, h.team_long_name AS home_name,
       m.away_team_api_id, a.team_long_name AS away_name,
       m.home_team_goal, m.away_team_goal
FROM Match AS m
LEFT JOIN League AS l ON l.id = m.league_id
LEFT JOIN Team AS h ON h.team_api_id = m.home_team_api_id
LEFT JOIN Team AS a ON a.team_api_id = m.away_team_api_id
"""


def _connect(database_path: Path) -> sqlite3.Connection:
    uri = database_path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _key(name: str) -> str:
    return " ".join(name.casefold().split())


def _check_id(value: int) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError("IDs must be positive integers")


def find_teams(database_path: Path, name: str) -> list[TeamCandidate]:
    """Return all exact long- or short-name matches without merging team IDs."""
    if not isinstance(name, str) or not _key(name) or len(name) > 100:
        raise ValueError("Provide a team name of at most 100 characters")

    wanted = _key(name)
    candidates: list[TeamCandidate] = []

    with closing(_connect(database_path)) as connection:
        teams = connection.execute(
            "SELECT team_api_id, team_long_name, team_short_name "
            "FROM Team ORDER BY team_api_id"
        ).fetchall()

        for team in teams:
            long_name = str(team["team_long_name"])
            short_name = team["team_short_name"]
            names = {
                _key(long_name),
                _key(str(short_name)) if short_name is not None else "",
            }
            if wanted not in names:
                continue

            team_id = int(team["team_api_id"])
            context = connection.execute(
                """
                SELECT DISTINCT m.league_id, l.name, m.season
                FROM Match AS m
                LEFT JOIN League AS l ON l.id = m.league_id
                WHERE m.home_team_api_id = ? OR m.away_team_api_id = ?
                """,
                (team_id, team_id),
            ).fetchall()

            leagues = tuple(
                sorted(
                    {
                        str(row["name"])
                        if row["name"] is not None
                        else f"League ID {row['league_id']}"
                        for row in context
                    }
                )
            )
            seasons = tuple(sorted({str(row["season"]) for row in context}))
            candidates.append(
                TeamCandidate(
                    team_id=team_id,
                    long_name=long_name,
                    short_name=(str(short_name) if short_name is not None else None),
                    leagues=leagues,
                    seasons=seasons,
                )
            )

    return candidates


def _record(row: sqlite3.Row) -> MatchRecord:
    return MatchRecord(
        match_id=int(row["id"]),
        league_id=int(row["league_id"]),
        league_name=str(row["name"]) if row["name"] is not None else None,
        season=str(row["season"]),
        match_date=datetime.fromisoformat(str(row["date"])).date(),
        home_team_id=int(row["home_team_api_id"]),
        home_team_name=(
            str(row["home_name"]) if row["home_name"] is not None else None
        ),
        away_team_id=int(row["away_team_api_id"]),
        away_team_name=(
            str(row["away_name"]) if row["away_name"] is not None else None
        ),
        home_goals=int(row["home_team_goal"]),
        away_goals=int(row["away_team_goal"]),
    )


def get_match(database_path: Path, match_id: int) -> MatchRecord | None:
    """Retrieve one result by its unique match ID."""
    _check_id(match_id)
    with closing(_connect(database_path)) as connection:
        row = connection.execute(
            _MATCH_SELECT + " WHERE m.id = ?", (match_id,)
        ).fetchone()
    return _record(row) if row is not None else None


def find_matches(
    database_path: Path,
    first_team_id: int,
    second_team_id: int,
    *,
    season: str | None = None,
    league_id: int | None = None,
) -> list[MatchRecord]:
    """Retrieve both home and away meetings between two resolved team IDs."""
    _check_id(first_team_id)
    _check_id(second_team_id)
    if first_team_id == second_team_id:
        raise ValueError("Select two different team IDs")
    if season is not None and (
        not isinstance(season, str) or fullmatch(r"[0-9]{4}/[0-9]{4}", season) is None
    ):
        raise ValueError("Season must have format YYYY/YYYY")
    if league_id is not None:
        _check_id(league_id)

    conditions = [
        "((m.home_team_api_id = ? AND m.away_team_api_id = ?) "
        "OR (m.home_team_api_id = ? AND m.away_team_api_id = ?))"
    ]
    parameters: list[int | str] = [
        first_team_id,
        second_team_id,
        second_team_id,
        first_team_id,
    ]
    if season is not None:
        conditions.append("m.season = ?")
        parameters.append(season)
    if league_id is not None:
        conditions.append("m.league_id = ?")
        parameters.append(league_id)

    sql = (
        _MATCH_SELECT
        + " WHERE "
        + " AND ".join(conditions)
        + " ORDER BY m.date, m.id LIMIT 51"
    )
    with closing(_connect(database_path)) as connection:
        rows = connection.execute(sql, parameters).fetchall()

    if len(rows) > 50:
        raise ValueError("Too many matches; specify a season or league")
    return [_record(row) for row in rows]
