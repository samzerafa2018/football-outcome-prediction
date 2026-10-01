from dataclasses import fields, replace
from datetime import date

from footballml.data import Match
from footballml.dataset import ModelInputs, build_examples


def test_examples_keep_matches_aligned_and_scores_out_of_inputs() -> None:
    training = Match(1, 1, "2013/2014", date(2014, 5, 18), 10, 20, 2, 0)
    validation = Match(2, 1, "2014/2015", date(2014, 7, 18), 10, 30, 0, 1)

    examples = build_examples([validation, training])

    assert [row.match_id for row in examples] == [1, 2]
    assert [row.target for row in examples] == ["H", "A"]
    assert examples[1].inputs.home_matches == 1
    assert examples[1].inputs.home_points_per_match == 3.0

    input_names = {field.name for field in fields(ModelInputs)}
    assert input_names.isdisjoint({"home_goals", "away_goals", "target"})

    revised = build_examples([replace(validation, home_goals=2), training])
    assert revised[1].inputs == examples[1].inputs
    assert revised[1].target == "H"
