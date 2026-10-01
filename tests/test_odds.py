import sqlite3
from pathlib import Path

import pytest

from footballml.data import TEST_SEASON
from footballml.evaluate_odds import _load_bet365


def test_bet365_normalizes_margin_and_excludes_unusable_rows(
    tmp_path: Path,
) -> None:
    database = tmp_path / "matches.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE Match "
            "(id INTEGER, season TEXT, B365H REAL, B365D REAL, B365A REAL)"
        )
        connection.executemany(
            "INSERT INTO Match VALUES (?, ?, ?, ?, ?)",
            [
                (1, TEST_SEASON, 1.8, 3.6, 3.6),
                (2, TEST_SEASON, 1.8, None, 3.6),
                (3, "2014/2015", 1.8, 3.6, 3.6),
            ],
        )

    probabilities = _load_bet365(database)
    assert set(probabilities) == {1}
    assert probabilities[1] == pytest.approx({"H": 0.5, "D": 0.25, "A": 0.25})
