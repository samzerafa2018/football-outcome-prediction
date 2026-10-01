from dataclasses import dataclass

from footballml.data import TEST_SEASON, TRAIN_SEASONS, VALIDATION_SEASON
from footballml.dataset import Example

# These dataset labels have the consistent YYYY/YYYY format.
SEASON_ORDER = tuple(sorted((*TRAIN_SEASONS, VALIDATION_SEASON, TEST_SEASON)))
SEASON_POSITION = {season: index for index, season in enumerate(SEASON_ORDER)}
VALIDATION_SEASONS = ("2012/2013", "2013/2014", VALIDATION_SEASON)


@dataclass(frozen=True, slots=True)
class SeasonFold:
    validation_season: str
    train: tuple[Example, ...]
    validation: tuple[Example, ...]


def rolling_validation_folds(examples: list[Example]) -> tuple[SeasonFold, ...]:
    """Use earlier seasons to predict each validation season."""
    unknown = {row.season for row in examples} - SEASON_POSITION.keys()
    if unknown:
        raise ValueError(f"Unexpected seasons: {sorted(unknown)}")

    folds: list[SeasonFold] = []
    for season in VALIDATION_SEASONS:
        cutoff = SEASON_POSITION[season]
        train = tuple(row for row in examples if SEASON_POSITION[row.season] < cutoff)
        validation = tuple(row for row in examples if row.season == season)
        if not train or not validation:
            raise ValueError(f"Missing training or validation data for {season}")

        folds.append(SeasonFold(season, train, validation))

    return tuple(folds)
