"""Small synthetic regressions for the two new data-facing paths."""

import json
import sqlite3
from contextlib import closing
from hashlib import sha256
from pathlib import Path

import pytest

from footballml.performance import league_summaries
from footballml.predictions import MODEL_VERSION, load_forecast


def test_forecast_archive_requires_matching_fixture_and_data(tmp_path: Path) -> None:
    database = tmp_path / "matches.sqlite"
    archive_path = tmp_path / "predictions.json"
    with closing(sqlite3.connect(database)) as connection:
        connection.executescript(
            """
            CREATE TABLE Team (team_api_id INTEGER, team_long_name TEXT);
            CREATE TABLE League (id INTEGER, name TEXT);
            CREATE TABLE Match (
                id INTEGER, league_id INTEGER, season TEXT, date TEXT,
                home_team_api_id INTEGER, away_team_api_id INTEGER,
                home_team_goal INTEGER, away_team_goal INTEGER
            );
            INSERT INTO Team VALUES (1, 'Home'), (2, 'Away');
            INSERT INTO League VALUES (9, 'League');
            INSERT INTO Match VALUES
                (12, 9, '2015/2016', '2016-01-01 00:00:00', 1, 2, 0, 3);
            """
        )
    archive = {
        "model_version": MODEL_VERSION,
        "train_cutoff": "2015-05-31",
        "test_season": "2015/2016",
        "data_sha256": sha256(database.read_bytes()).hexdigest(),
        "predictions": {
            "12": {
                "date": "2016-01-01",
                "league_id": 9,
                "home_team_id": 1,
                "away_team_id": 2,
                "H": 0.5,
                "D": 0.3,
                "A": 0.2,
            }
        },
    }
    archive_path.write_text(json.dumps(archive), encoding="utf-8")

    forecast = load_forecast(database, archive_path, 12)
    assert forecast is not None
    assert forecast.probabilities == {"H": 0.5, "D": 0.3, "A": 0.2}
    assert forecast.train_cutoff == "2015-05-31"

    archive["predictions"]["12"]["away_team_id"] = 1
    archive_path.write_text(json.dumps(archive), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match the recorded fixture"):
        load_forecast(database, archive_path, 12)

    archive["predictions"]["12"]["away_team_id"] = 2
    with closing(sqlite3.connect(database)) as connection:
        connection.execute("UPDATE Match SET home_team_goal = 1 WHERE id = 12")
        connection.commit()
    archive_path.write_text(json.dumps(archive), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match this model and database"):
        load_forecast(database, archive_path, 12)


def test_league_ranking_uses_points_per_match_not_total_points(tmp_path: Path) -> None:
    database = tmp_path / "matches.sqlite"
    with closing(sqlite3.connect(database)) as connection:
        connection.executescript(
            """
            CREATE TABLE Team (team_api_id INTEGER, team_long_name TEXT);
            CREATE TABLE League (id INTEGER, name TEXT);
            CREATE TABLE Match (
                id INTEGER, league_id INTEGER, season TEXT, date TEXT,
                home_team_api_id INTEGER, away_team_api_id INTEGER,
                home_team_goal INTEGER, away_team_goal INTEGER
            );
            INSERT INTO Team VALUES
                (1, 'Leader'), (2, 'A'), (3, 'B'), (4, 'C'),
                (5, 'Draw A'), (6, 'Draw B'), (7, 'Draw C'), (8, 'Draw D');
            INSERT INTO League VALUES (9, 'Winning League'), (10, 'Draw League');
            INSERT INTO Match VALUES
                (1, 9, '2015/2016', '2016-01-01', 1, 2, 1, 0),
                (2, 9, '2015/2016', '2016-01-02', 2, 3, 0, 0),
                (3, 9, '2015/2016', '2016-01-03', 3, 4, 0, 0),
                (6, 9, '2015/2016', '2016-01-04', 4, 2, 0, 0),
                (7, 9, '2015/2016', '2016-01-05', 2, 3, 0, 0),
                (8, 9, '2015/2016', '2016-01-06', 3, 4, 0, 0),
                (4, 10, '2015/2016', '2016-01-01', 5, 6, 0, 0),
                (5, 10, '2015/2016', '2016-01-02', 7, 8, 1, 1);
            """
        )

    ranked = league_summaries(database)
    assert [(row.league, row.top_quarter_ppm) for row in ranked] == [
        ("Winning League", 3.0),
        ("Draw League", 1.0),
    ]
    assert (ranked[0].top_team, ranked[0].top_team_count, ranked[0].team_count) == (
        "Leader",
        1,
        4,
    )
