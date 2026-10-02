"""Descriptive team and league performance from recorded matches."""

import sqlite3
from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from re import fullmatch

from footballml.data import TEST_SEASON


@dataclass(frozen=True, slots=True)
class LeagueSummary:
    league: str
    top_team: str
    top_team_ppm: float
    top_quarter_ppm: float
    top_team_count: int
    team_count: int


def league_summaries(
    database_path: Path, season: str = TEST_SEASON
) -> list[LeagueSummary]:
    """Rank leagues by the mean points per match of their top quarter."""
    if fullmatch(r"[0-9]{4}/[0-9]{4}", season) is None:
        raise ValueError("Season must have format YYYY/YYYY")

    uri = database_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        fixtures = connection.execute(
            """
            SELECT l.name, m.home_team_api_id, m.away_team_api_id,
                   m.home_team_goal, m.away_team_goal
            FROM Match AS m JOIN League AS l ON l.id = m.league_id
            WHERE m.season = ?
            """,
            (season,),
        ).fetchall()
        names = dict(connection.execute("SELECT team_api_id, team_long_name FROM Team"))

    if not fixtures:
        raise ValueError("No recorded matches for that season")

    # Each entry is [matches played, points earned].
    records: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])
    for league, home_id, away_id, home_goals, away_goals in fixtures:
        home = records[str(league), int(home_id)]
        away = records[str(league), int(away_id)]
        home[0] += 1
        away[0] += 1
        if home_goals > away_goals:
            home[1] += 3
        elif home_goals < away_goals:
            away[1] += 3
        else:
            home[1] += 1
            away[1] += 1

    by_league: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for (league, team_id), (played, points) in records.items():
        by_league[league].append((team_id, points / played))

    summaries = []
    for league, teams in by_league.items():
        teams.sort(key=lambda item: (-item[1], item[0]))
        count = ceil(len(teams) / 4)
        leader_id, leader_ppm = teams[0]
        summaries.append(
            LeagueSummary(
                league=league,
                top_team=str(names.get(leader_id) or f"Team ID {leader_id}"),
                top_team_ppm=leader_ppm,
                top_quarter_ppm=sum(ppm for _, ppm in teams[:count]) / count,
                top_team_count=count,
                team_count=len(teams),
            )
        )
    return sorted(summaries, key=lambda row: (-row.top_quarter_ppm, row.league))


def format_league_summaries(
    summaries: list[LeagueSummary], season: str = TEST_SEASON
) -> str:
    """Label the ranking as a within-league statistic, not league strength."""
    lines = [f"{season}: top-quarter teams' mean points per recorded match"]
    for row in summaries:
        lines.append(
            f"{row.league}: {row.top_quarter_ppm:.3f} "
            f"(top {row.top_team_count}/{row.team_count}; "
            f"leader {row.top_team} {row.top_team_ppm:.3f})"
        )
    lines.append(
        "This compares domestic points concentration, not league strength. "
        "Teams mostly played opponents in their own leagues."
    )
    return "\n".join(lines)
