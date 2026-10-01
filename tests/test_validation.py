from datetime import date

from footballml.dataset import Example, ModelInputs
from footballml.validation import rolling_validation_folds


def example(match_id: int, season: str) -> Example:
    return Example(
        match_id=match_id,
        match_date=date(int(season[:4]), 8, 1),
        season=season,
        inputs=ModelInputs(1, 10, 20, 0, 0, 0.0, 0.0, 0.0, 0.0),
        target="H",
    )


def test_folds_expand_forward_and_exclude_final_test() -> None:
    examples = [
        example(5, "2015/2016"),
        example(4, "2014/2015"),
        example(3, "2013/2014"),
        example(2, "2012/2013"),
        example(1, "2008/2009"),
    ]

    folds = rolling_validation_folds(examples)

    assert [fold.validation_season for fold in folds] == [
        "2012/2013",
        "2013/2014",
        "2014/2015",
    ]
    assert [{row.match_id for row in fold.train} for fold in folds] == [
        {1},
        {1, 2},
        {1, 2, 3},
    ]
    assert [{row.match_id for row in fold.validation} for fold in folds] == [
        {2},
        {3},
        {4},
    ]
