"""Command-line lookup of recorded football match results."""

import argparse
from pathlib import Path

from footballml.answers import answer_match, answer_team_ids, answer_teams
from footballml.data import TEST_SEASON
from footballml.lookup import find_matches, find_teams
from footballml.performance import format_league_summaries, league_summaries
from footballml.predictions import (
    DEFAULT_ARCHIVE,
    format_forecast,
    load_forecast,
    save_heldout_predictions,
)


def _print_forecast(database_path: Path, archive_path: Path, match_id: int) -> None:
    forecast = load_forecast(database_path, archive_path, match_id)
    print(
        format_forecast(forecast)
        if forecast is not None
        else "No stored 2015/2016 forecast for that match ID."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up recorded 2008–2016 results")
    parser.add_argument(
        "--db", type=Path, default=Path("Data/database.sqlite/database.sqlite")
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    commands = parser.add_subparsers(dest="command", required=True)

    match = commands.add_parser("match", help="Find one match by ID")
    match.add_argument("match_id", type=int)

    teams = commands.add_parser("teams", help="Find matches by exact team names")
    teams.add_argument("first_team")
    teams.add_argument("second_team")

    team_ids = commands.add_parser("team-ids", help="Resolve ambiguous team names")
    team_ids.add_argument("first_team_id", type=int)
    team_ids.add_argument("second_team_id", type=int)

    commands.add_parser("build-forecasts", help="Save held-out 2015/2016 predictions")
    forecast = commands.add_parser(
        "forecast", help="Show a stored forecast by match ID"
    )
    forecast.add_argument("match_id", type=int)
    forecast_teams = commands.add_parser(
        "forecast-teams", help="Find stored forecasts by exact team names"
    )
    forecast_teams.add_argument("first_team")
    forecast_teams.add_argument("second_team")
    performance = commands.add_parser(
        "league-performance", help="Compare top-quarter points per match"
    )
    performance.add_argument("--season", default=TEST_SEASON)

    for command in (teams, team_ids):
        command.add_argument("--season")
        command.add_argument("--league-id", type=int)

    args = parser.parse_args()
    if args.command == "build-forecasts":
        count = save_heldout_predictions(args.db, args.archive)
        print(f"Saved {count} held-out forecasts to {args.archive}")
        return
    if args.command == "league-performance":
        summaries = league_summaries(args.db, args.season)
        print(format_league_summaries(summaries, args.season))
        return
    if args.command == "forecast":
        _print_forecast(args.db, args.archive, args.match_id)
        return
    if args.command == "forecast-teams":
        first = [
            team
            for team in find_teams(args.db, args.first_team)
            if TEST_SEASON in team.seasons
        ]
        second = [
            team
            for team in find_teams(args.db, args.second_team)
            if TEST_SEASON in team.seasons
        ]
        if len(first) != 1 or len(second) != 1:
            print(
                "Team names must each identify one team in 2015/2016; use exact names."
            )
            return
        if first[0].team_id == second[0].team_id:
            print("Choose two different teams.")
            return
        matches = find_matches(
            args.db, first[0].team_id, second[0].team_id, season=TEST_SEASON
        )
        if not matches:
            print("No meeting between those teams was recorded in 2015/2016.")
        elif len(matches) > 1:
            print("Choose a fixture and run 'forecast MATCH_ID':")
            for fixture in matches:
                print(
                    f"{fixture.match_date} | {fixture.league_name} | "
                    f"{fixture.home_team_name} vs {fixture.away_team_name} "
                    f"| match ID {fixture.match_id}"
                )
        else:
            _print_forecast(args.db, args.archive, matches[0].match_id)
        return

    if args.command == "match":
        answer = answer_match(args.db, args.match_id)
    elif args.command == "teams":
        answer = answer_teams(
            args.db,
            args.first_team,
            args.second_team,
            season=args.season,
            league_id=args.league_id,
        )
    else:
        answer = answer_team_ids(
            args.db,
            args.first_team_id,
            args.second_team_id,
            season=args.season,
            league_id=args.league_id,
        )
    print(answer.text)


if __name__ == "__main__":
    main()
