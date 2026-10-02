import sqlite3
from contextlib import closing
from pathlib import Path

from footballml.lookup import find_matches, find_teams, get_match


def test_duplicate_names_and_same_day_matches(tmp_path: Path) -> None:
    database = tmp_path / "matches.sqlite"
    with closing(sqlite3.connect(database)) as connection:
        connection.executescript(
            """
            CREATE TABLE Team (
                team_api_id INTEGER,
                team_long_name TEXT,
                team_short_name TEXT
            );
            CREATE TABLE League (id INTEGER, name TEXT);
            CREATE TABLE Match (
                id INTEGER, league_id INTEGER, season TEXT, date TEXT,
                home_team_api_id INTEGER, away_team_api_id INTEGER,
                home_team_goal INTEGER, away_team_goal INTEGER
            );

            INSERT INTO Team VALUES
                (1, 'Mouscron', 'MOU'),
                (2, 'Mouscron', 'MOP'),
                (3, 'Other FC', 'OTH');
            INSERT INTO League VALUES (9, 'Example League');
            INSERT INTO Match VALUES
                (10, 9, '2015/2016', '2016-01-01 00:00:00', 1, 3, 1, 0),
                (11, 9, '2015/2016', '2016-01-01 00:00:00', 3, 1, 2, 1),
                (12, 9, '2015/2016', '2016-01-02 00:00:00', 2, 3, 0, 0);
            """
        )

    assert [team.team_id for team in find_teams(database, "mouscron")] == [1, 2]
    assert [
        match.match_id for match in find_matches(database, 1, 3, season="2015/2016")
    ] == [10, 11]
    assert [match.match_id for match in find_matches(database, 2, 3)] == [12]

    match = get_match(database, 11)
    assert match is not None
    assert (match.match_id, match.home_goals, match.away_goals) == (11, 2, 1)
    assert (match.league_name, match.home_team_id, match.away_team_id) == (
        "Example League",
        3,
        1,
    )
