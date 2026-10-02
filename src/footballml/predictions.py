"""Save and retrieve held-out pre-match probabilities."""

import json
from dataclasses import dataclass
from hashlib import file_digest
from math import isfinite
from pathlib import Path

from footballml.baseline import OUTCOMES
from footballml.data import (
    TEST_SEASON,
    TRAIN_SEASONS,
    VALIDATION_SEASON,
    Outcome,
    load_matches,
)
from footballml.lookup import MatchRecord, get_match

FORM_WINDOW = 40
MODEL_C = 0.03
MODEL_VERSION = f"logistic-v1-w{FORM_WINDOW}-c{MODEL_C}"
DEFAULT_ARCHIVE = Path("Data/heldout_predictions.json")


@dataclass(frozen=True, slots=True)
class Forecast:
    match: MatchRecord
    probabilities: dict[Outcome, float]
    model_version: str
    train_cutoff: str


def _data_hash(database_path: Path) -> str:
    with database_path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


def save_heldout_predictions(database_path: Path, archive_path: Path) -> int:
    """Fit on seasons before 2015/2016 and save only held-out forecasts."""
    from footballml.dataset import build_examples
    from footballml.logistic import fit_model, predict_probabilities

    examples = build_examples(load_matches(database_path), window=FORM_WINDOW)
    train = [
        row
        for row in examples
        if row.season in TRAIN_SEASONS or row.season == VALIDATION_SEASON
    ]
    test = [row for row in examples if row.season == TEST_SEASON]
    if not train or not test or len(train) + len(test) != len(examples):
        raise ValueError("Unexpected season split")
    if max(row.match_date for row in train) >= min(row.match_date for row in test):
        raise ValueError("Training must precede testing")

    probabilities = predict_probabilities(fit_model(train, c=MODEL_C), test)
    records = {
        str(row.match_id): {
            "date": row.match_date.isoformat(),
            "league_id": row.inputs.league_id,
            "home_team_id": row.inputs.home_team_id,
            "away_team_id": row.inputs.away_team_id,
            **probs,
        }
        for row, probs in zip(test, probabilities, strict=True)
    }
    archive = {
        "model_version": MODEL_VERSION,
        "train_cutoff": max(row.match_date for row in train).isoformat(),
        "test_season": TEST_SEASON,
        "data_sha256": _data_hash(database_path),
        "predictions": records,
    }
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(json.dumps(archive, indent=2) + "\n", encoding="utf-8")
    return len(records)


def load_forecast(
    database_path: Path, archive_path: Path, match_id: int
) -> Forecast | None:
    """Check archive provenance and fixture identity before displaying a forecast."""
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    if (
        archive["model_version"] != MODEL_VERSION
        or archive["test_season"] != TEST_SEASON
        or archive["data_sha256"] != _data_hash(database_path)
    ):
        raise ValueError("Prediction archive does not match this model and database")

    match = get_match(database_path, match_id)
    if match is None or match.season != TEST_SEASON:
        return None
    record = archive["predictions"].get(str(match_id))
    if record is None or (
        record["date"],
        record["league_id"],
        record["home_team_id"],
        record["away_team_id"],
    ) != (
        match.match_date.isoformat(),
        match.league_id,
        match.home_team_id,
        match.away_team_id,
    ):
        raise ValueError("Prediction does not match the recorded fixture")

    probabilities: dict[Outcome, float] = {
        label: float(record[label]) for label in OUTCOMES
    }
    if (
        not all(isfinite(p) and 0 <= p <= 1 for p in probabilities.values())
        or abs(sum(probabilities.values()) - 1) > 1e-8
    ):
        raise ValueError("Invalid prediction probabilities")
    return Forecast(
        match, probabilities, archive["model_version"], archive["train_cutoff"]
    )


def format_forecast(forecast: Forecast) -> str:
    """Display the historical forecast without revealing the recorded result."""
    match = forecast.match
    probs = forecast.probabilities
    home = match.home_team_name or f"Team ID {match.home_team_id}"
    away = match.away_team_name or f"Team ID {match.away_team_id}"
    league = match.league_name or f"League ID {match.league_id}"

    if probs["H"] > probs["A"]:
        comparison = (
            f"Model win edge: {home} by "
            f"{(probs['H'] - probs['A']) * 100:.1f} percentage points."
        )
    elif probs["A"] > probs["H"]:
        comparison = (
            f"Model win edge: {away} by "
            f"{(probs['A'] - probs['H']) * 100:.1f} percentage points."
        )
    else:
        comparison = "The teams have equal estimated win probabilities."

    return (
        f"{match.match_date} | {league} | {home} vs {away} "
        f"| match ID {match.match_id}\n"
        f"{home} win: {probs['H']:.1%}; draw: {probs['D']:.1%}; "
        f"{away} win: {probs['A']:.1%}.\n"
        f"Loss: {home} {probs['A']:.1%}; {away} {probs['H']:.1%}.\n"
        f"{comparison}\n"
        f"Model: {forecast.model_version}; trained through {forecast.train_cutoff}. "
        "Historical pre-match forecast, not a current prediction."
    )
