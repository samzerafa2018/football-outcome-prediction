# Data card: European football match database

## Source and scope

Source: [European Soccer Database by Hugo Mathien](https://www.kaggle.com/datasets/hugomathien/soccer). The local SQLite file contains 25,979 matches across 11 domestic leagues and eight seasons, from 2008/2009 through 2015/2016. The raw database is excluded from Git.

Local database SHA-256:
`4DF8569777D59FDD690754B1CC8CA1F7989BAF65F2EADDD0F1368285F11139A9`

This hash identifies the database used for the reported audit and results; it is not a substitute for a copy of the data. Redistribution and usage terms should be checked against the original source.

## Coverage audit

In 2015/2016, the database contains 3,326 matches. Its league counts fit the expected regular-season formats, but **this does not mean every competition phase is included**:

- Belgium contains 240 matches and ends on 13 March 2016. Its subsequent championship playoff is absent.
- Poland contains 240 matches and ends on 9 April 2016. Its 2015/2016 competition had 37 rounds, including a final phase; the database contains the 30-round regular season and omits the 56 final-phase matches.
- Italy contains 380 matches in 2015/2016. In the preceding validation season, 2014/2015, its count is 379 rather than the expected 380.

The audit compares counts and date ranges. It has not checked every fixture against an external results list or established that all other seasons are complete. The existing 2015/2016 test evaluation is retained, with these coverage limits disclosed.

Sources: [Polish football federation, 2015/2016 format](https://www.pzpn.pl/federacja/aktualnosci/2015-04-21/przyjeto-regulamin-rozgrywek-ekstraklasy-na-sezon-2015-2016); [UEFA, Belgian 2015/2016 championship playoff](https://www.uefa.com/news-media/news/022d-0e9452deae83-a70039b6c6f8-1000--club-brugge-end-11-year-belgian-title-wait/).

## Use in this project

The outcome is home win, draw, or away win. Pre-match form uses results dated strictly before each match's calendar date; matches on the same date cannot inform one another. Historical bookmaker odds are used only for a separate benchmark, and their pre-kickoff snapshot time has not been established.

The database ends in 2016. It cannot answer questions about later matches or support claims about current forecasting performance.
