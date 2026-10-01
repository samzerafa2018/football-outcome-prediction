from dataclasses import replace
from datetime import date

from footballml.data import Match
from footballml.features import build_form_features


def test_same_day_results_are_not_used_as_history() -> None:
    first_day = date(2010, 8, 1)
    next_day = date(2010, 8, 2)
    matches = [
        Match(1, 1, "2010/2011", first_day, 10, 20, 3, 0),
        Match(2, 1, "2010/2011", first_day, 10, 30, 0, 1),
        Match(3, 1, "2010/2011", next_day, 10, 40, 2, 2),
    ]

    features = {row.match_id: row for row in build_form_features(matches)}

    assert features[1].home_matches == 0
    assert features[2].home_matches == 0
    assert features[2].home_points_per_match == 0.0
    assert features[3].home_matches == 2
    assert features[3].home_points_per_match == 1.5


def test_window_uses_recent_results_from_home_and_away_games() -> None:
    matches = [
        Match(1, 1, "2010/2011", date(2010, 8, 1), 10, 20, 2, 0),
        Match(2, 1, "2010/2011", date(2010, 8, 2), 30, 10, 1, 1),
        Match(3, 1, "2010/2011", date(2010, 8, 3), 40, 10, 2, 0),
        Match(4, 1, "2010/2011", date(2010, 8, 4), 10, 50, 0, 0),
    ]
    features = {row.match_id: row for row in build_form_features(matches, window=2)}

    assert features[2].away_points_per_match == 3.0
    assert features[4].home_matches == 2
    assert features[4].home_points_per_match == 0.5


def test_current_result_cannot_change_its_own_features() -> None:
    first = Match(1, 1, "2010/2011", date(2010, 8, 1), 10, 20, 2, 0)
    second = Match(2, 1, "2010/2011", date(2010, 8, 2), 10, 30, 0, 2)
    third = Match(3, 1, "2010/2011", date(2010, 8, 3), 10, 40, 1, 1)

    original = {
        row.match_id: row for row in build_form_features([first, second, third])
    }
    revised = {
        row.match_id: row
        for row in build_form_features(
            [first, replace(second, home_goals=3, away_goals=0), third]
        )
    }

    assert original[2] == revised[2]
    assert original[3].home_points_per_match == 1.5
    assert revised[3].home_points_per_match == 3.0
