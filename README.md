# Football Match Outcome Prediction

Predict pre-match probabilities for a home win, draw, or away win using historical European football data.

## Status

In development. The Python package is installable; data analysis, models, and evaluation have not been completed.

## Data

Source: *European Soccer Database* by Hugo Mathien. The local SQLite file is at `Data/database.sqlite/database.sqlite`. Raw data is excluded from Git.

## Planned approach

Use only information available before each match. Compare simple baselines with trained models using chronological splits, probability metrics, and calibration checks. Treat bookmaker odds as a benchmark.

## Local setup

From the project folder in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -c "import footballml; print(footballml.__file__)"
```
