"""Small, read-only browser for recorded results and saved forecasts."""

import sqlite3
from contextlib import closing
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from footballml.data import TEST_SEASON, Outcome
from footballml.lookup import MatchRecord, find_matches
from footballml.matchup import (
    FULL_MODEL_VERSION,
    FullModel,
    fit_full_model,
    predict_matchup,
)
from footballml.performance import league_summaries
from footballml.predictions import load_forecast

ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "Data/database.sqlite/database.sqlite"
ARCHIVE = ROOT / "Data/heldout_predictions.json"


@st.cache_data(show_spinner=False)
def seasons(database: Path) -> list[str]:
    uri = database.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        return [
            row[0]
            for row in db.execute("SELECT DISTINCT season FROM Match ORDER BY season")
        ]


@st.cache_data(show_spinner=False)
def teams(database: Path, season: str) -> list[tuple[int, str]]:
    uri = database.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        return [
            (int(team_id), str(name))
            for team_id, name in db.execute(
                """SELECT team_api_id, team_long_name FROM Team
                   WHERE team_api_id IN (
                       SELECT home_team_api_id FROM Match WHERE season = ?
                       UNION
                       SELECT away_team_api_id FROM Match WHERE season = ?
                   ) ORDER BY team_long_name, team_api_id""",
                (season, season),
            )
        ]


def fixture_label(match: MatchRecord) -> str:
    return (
        f"{match.match_date} · {match.league_name} · "
        f"{match.home_team_name} vs {match.away_team_name} · ID {match.match_id}"
    )


def outcome_chart(home: str, away: str, probabilities: dict[Outcome, float]) -> None:
    """Show three outcomes against a full 0–100% probability scale."""
    rows = [
        {"Outcome": f"{home} win", "Probability": probabilities["H"]},
        {"Outcome": "Draw", "Probability": probabilities["D"]},
        {"Outcome": f"{away} win", "Probability": probabilities["A"]},
    ]
    chart = (
        alt.Chart(pd.DataFrame(rows))
        .mark_bar(color="#165DCC", cornerRadiusEnd=4)
        .encode(
            x=alt.X(
                "Probability:Q",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            y=alt.Y("Outcome:N", sort=[row["Outcome"] for row in rows], title=None),
            tooltip=[
                alt.Tooltip("Outcome:N"),
                alt.Tooltip("Probability:Q", format=".1%"),
            ],
        )
        .properties(height=160)
    )
    st.altair_chart(chart, width="stretch")


@st.cache_data(show_spinner=False)
def matchup_options(
    database: Path,
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    uri = database.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        teams = [
            (int(team_id), str(name))
            for team_id, name in db.execute(
                "SELECT team_api_id, team_long_name FROM Team "
                "ORDER BY team_long_name, team_api_id"
            )
        ]
        leagues = [
            (int(league_id), str(name))
            for league_id, name in db.execute(
                "SELECT id, name FROM League ORDER BY name"
            )
        ]
    return teams, leagues


@st.cache_resource(show_spinner="Fitting the model on historical matches...")
def trained_model(database: Path) -> FullModel:
    return fit_full_model(database)


st.set_page_config(page_title="Football match explorer", layout="centered")
st.title("Football match explorer")
st.caption("Recorded 2008/2009–2015/2016 matches. No live data or current forecasts.")

if not DATABASE.is_file():
    st.error("Place the SQLite database at Data/database.sqlite/database.sqlite.")
    st.stop()

page = st.radio(
    "Explore",
    ["Results", "Predict a matchup", "Historical forecasts", "League comparison"],
    horizontal=True,
)
season_options = seasons(DATABASE)
if not season_options:
    st.error("The database has no recorded seasons.")
    st.stop()

if page == "Predict a matchup":
    st.caption(
        "A hypothetical matchup immediately after the final recorded match in 2016. "
        "The model learns from all 25,979 matches. These are not current forecasts."
    )
    all_teams, all_leagues = matchup_options(DATABASE)
    with st.form("new_matchup"):
        first_col, second_col = st.columns(2)
        with first_col:
            home = st.selectbox(
                "Home team",
                all_teams,
                index=None,
                placeholder="Choose a team",
                format_func=lambda team: f"{team[1]} (ID {team[0]})",
            )
        with second_col:
            away = st.selectbox(
                "Away team",
                all_teams,
                index=None,
                placeholder="Choose a team",
                format_func=lambda team: f"{team[1]} (ID {team[0]})",
            )
        league = st.selectbox(
            "Assumed league",
            all_leagues,
            index=None,
            placeholder="Choose a league",
            format_func=lambda item: item[1],
        )
        submitted = st.form_submit_button("Estimate probabilities")
    if submitted:
        if home is None or away is None or league is None:
            st.info("Choose two teams and an assumed league.")
        elif home[0] == away[0]:
            st.info("Choose two different teams.")
        else:
            fitted = trained_model(DATABASE)
            probabilities = predict_matchup(fitted, league[0], home[0], away[0])
            h, d, a = st.columns(3)
            h.metric(f"{home[1]} win", f"{probabilities['H']:.1%}")
            d.metric("Draw", f"{probabilities['D']:.1%}")
            a.metric(f"{away[1]} win", f"{probabilities['A']:.1%}")
            outcome_chart(home[1], away[1], probabilities)
            st.caption(
                f"{league[1]} (assumed) · {FULL_MODEL_VERSION} · "
                f"{fitted.training_matches:,} matches through {fitted.trained_through}"
            )
            st.info(
                "Historical snapshot only. Teams, leagues, and form may have "
                "changed since 2016. Each team's loss probability is the other "
                "team's win probability."
            )
elif page == "League comparison":
    season = st.selectbox("Season", season_options, index=len(season_options) - 1)
    st.caption(
        "Top quarter of teams by points per recorded match, averaged within each "
        "league. This measures domestic points concentration, not league strength."
    )
    summaries = league_summaries(DATABASE, season)
    st.bar_chart(
        [
            {"League": row.league, "Top-quarter PPM": row.top_quarter_ppm}
            for row in summaries
        ],
        x="League",
        y="Top-quarter PPM",
        horizontal=True,
        sort=False,
        height=420,
        color="#165DCC",
    )
    with st.expander("Show exact figures"):
        st.table(
            [
                {
                    "League": row.league,
                    "Top-quarter PPM": f"{row.top_quarter_ppm:.3f}",
                    "Leader": row.top_team,
                    "Leader PPM": f"{row.top_team_ppm:.3f}",
                }
                for row in summaries
            ]
        )
else:
    forecast_mode = page == "Historical forecasts"
    if forecast_mode:
        st.caption(
            "Stored predictions for the held-out 2015/2016 season. "
            "The recorded result is hidden on this page."
        )
        season = TEST_SEASON
        if not ARCHIVE.is_file():
            st.info(
                "Generate the archive once from the project root: "
                "`.\\.venv\\Scripts\\python.exe -m footballml.query build-forecasts`"
            )
            st.stop()
    else:
        season = st.selectbox("Season", season_options, index=len(season_options) - 1)

    choices = teams(DATABASE, season)
    first_col, second_col = st.columns(2)
    with first_col:
        first = st.selectbox(
            "First team",
            choices,
            index=None,
            placeholder="Choose a team",
            format_func=lambda team: f"{team[1]} (ID {team[0]})",
        )
    with second_col:
        second = st.selectbox(
            "Second team",
            choices,
            index=None,
            placeholder="Choose a team",
            format_func=lambda team: f"{team[1]} (ID {team[0]})",
        )

    if first is not None and second is not None:
        if first[0] == second[0]:
            st.info("Choose two different teams.")
        else:
            matches = find_matches(DATABASE, first[0], second[0], season=season)
            if not matches:
                st.info("No recorded meeting for this pairing and season.")
            else:
                match = st.selectbox("Fixture", matches, format_func=fixture_label)
                if match is not None:
                    st.subheader(f"{match.home_team_name} vs {match.away_team_name}")
                    st.caption(
                        f"{match.match_date} · {match.league_name} · "
                        f"ID {match.match_id}"
                    )
                    if forecast_mode:
                        try:
                            forecast = load_forecast(DATABASE, ARCHIVE, match.match_id)
                        except (OSError, ValueError, KeyError) as exc:
                            st.error(f"Could not verify the forecast archive: {exc}")
                            st.stop()
                        if forecast is None:
                            st.info("No stored forecast for this fixture.")
                        else:
                            home, draw, away = st.columns(3)
                            home.metric(
                                f"{match.home_team_name} win",
                                f"{forecast.probabilities['H']:.1%}",
                            )
                            draw.metric("Draw", f"{forecast.probabilities['D']:.1%}")
                            away.metric(
                                f"{match.away_team_name} win",
                                f"{forecast.probabilities['A']:.1%}",
                            )
                            outcome_chart(
                                match.home_team_name or f"Team ID {match.home_team_id}",
                                match.away_team_name or f"Team ID {match.away_team_id}",
                                forecast.probabilities,
                            )
                            st.caption(
                                f"Model {forecast.model_version} · trained through "
                                f"{forecast.train_cutoff} · historical pre-match "
                                "forecast"
                            )
                    else:
                        st.metric(
                            "Recorded score", f"{match.home_goals}–{match.away_goals}"
                        )
