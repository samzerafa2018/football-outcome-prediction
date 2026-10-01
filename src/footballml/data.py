import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, slots=True)
class Match:
    match_id: int
    league_id: int
    season: str
    match_date: date
    home_team_id: int
    away_team_id: int
    home_goals: int
    away_goals: int


Outcome = Literal["H", "D", "A"]


def outcome_for(match: Match) -> Outcome:
    """Return home win, draw, or away win from the final score."""
    if match.home_goals > match.away_goals:
        return "H"
    if match.home_goals < match.away_goals:
        return "A"
    return "D"


TRAIN_SEASONS = frozenset(
    {
        "2008/2009",
        "2009/2010",
        "2010/2011",
        "2011/2012",
        "2012/2013",
        "2013/2014",
    }
)
VALIDATION_SEASON = "2014/2015"
TEST_SEASON = "2015/2016"


def split_matches(
    matches: list[Match],
) -> tuple[list[Match], list[Match], list[Match]]:
    """Split matches into training, validation, and final test seasons."""
    train: list[Match] = []
    validation: list[Match] = []
    test: list[Match] = []

    for match in matches:
        if match.season in TRAIN_SEASONS:
            train.append(match)
        elif match.season == VALIDATION_SEASON:
            validation.append(match)
        elif match.season == TEST_SEASON:
            test.append(match)
        else:
            raise ValueError(f"Unexpected season: {match.season}")

    return train, validation, test


def load_matches(database_path: Path) -> list[Match]:
    """Read the core match fields without changing the SQLite database."""
    uri = database_path.resolve().as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as connection:
        rows = connection.execute(
            """
            SELECT id, league_id, season, date,
                   home_team_api_id, away_team_api_id,
                   home_team_goal, away_team_goal
            FROM Match
            ORDER BY date, id
            """
        )
        return [
            Match(
                match_id=int(row[0]),
                league_id=int(row[1]),
                season=str(row[2]),
                match_date=datetime.fromisoformat(str(row[3])).date(),
                home_team_id=int(row[4]),
                away_team_id=int(row[5]),
                home_goals=int(row[6]),
                away_goals=int(row[7]),
            )
            for row in rows
        ]
