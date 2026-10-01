import sqlite3
from contextlib import closing
from math import isfinite
from pathlib import Path

from footballml.baseline import OUTCOMES, evaluate_prior, fit_prior
from footballml.data import (
    TEST_SEASON,
    TRAIN_SEASONS,
    VALIDATION_SEASON,
    Outcome,
    load_matches,
)
from footballml.dataset import build_examples
from footballml.evaluate_logistic import score_predictions
from footballml.logistic import fit_model, predict_probabilities


def _load_bet365(database_path: Path) -> dict[int, dict[Outcome, float]]:
    uri = database_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        rows = connection.execute(
            """
            SELECT id, B365H, B365D, B365A
            FROM Match
            WHERE season = ?
              AND B365H > 1 AND B365D > 1 AND B365A > 1
            """,
            (TEST_SEASON,),
        ).fetchall()

    probabilities: dict[int, dict[Outcome, float]] = {}
    for match_id, home, draw, away in rows:
        odds = (float(home), float(draw), float(away))
        if not all(isfinite(value) for value in odds):
            continue
        weights = [1 / value for value in odds]
        total = sum(weights)
        probabilities[int(match_id)] = dict(
            zip(OUTCOMES, (weight / total for weight in weights), strict=True)
        )
    return probabilities


def main() -> None:
    database_path = Path("Data/database.sqlite/database.sqlite")
    examples = build_examples(load_matches(database_path))
    train = [
        row
        for row in examples
        if row.season in TRAIN_SEASONS or row.season == VALIDATION_SEASON
    ]
    test = [row for row in examples if row.season == TEST_SEASON]
    if not train or not test or len(train) + len(test) != len(examples):
        raise ValueError("Unexpected season split")

    odds = _load_bet365(database_path)
    matched = [row for row in test if row.match_id in odds]
    if not matched:
        raise ValueError("No test matches have valid Bet365 odds")

    baseline = evaluate_prior(matched, fit_prior(train))
    model = fit_model(train)
    logistic = score_predictions(matched, predict_probabilities(model, matched))
    bookmaker = score_predictions(matched, [odds[row.match_id] for row in matched])

    print(f"Matched test matches: {len(matched)}/{len(test)}")
    for name, (accuracy, log_loss, brier) in (
        ("Training-prior baseline", baseline),
        ("Selected logistic model", logistic),
        ("Bet365 normalized odds", bookmaker),
    ):
        print(
            f"{name}: accuracy={accuracy:.4f}, "
            f"log_loss={log_loss:.4f}, brier={brier:.4f}"
        )


if __name__ == "__main__":
    main()
