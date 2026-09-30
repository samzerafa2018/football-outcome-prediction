# Decisions log

## 2026-09-30 — Treat match timestamps as calendar dates

**Evidence:** All 25,979 `Match.date` values have the time `00:00:00`.

**Decision:** For a match on date D, historical features may use results only from dates earlier than D. Match IDs and row order do not establish kick-off order.

**Reason:** The recorded time cannot tell us which same-day match finished first. Using a same-day result could leak information unavailable before kick-off.

**Tradeoff:** We may omit a legitimately earlier same-day result.

**Verification:** Test that a match's features exclude its own result, all later results, and every result dated the same day.
