# Nomos Block Explorer

## Assumptions
There are a few assumptions made to facilitate the development of the PoC:
- One block per slot.
- If a range has been backfilled, it has been fully successfully backfilled.
- Backfilling strategy assumes there's, at most, one gap to fill.

## TODO
- Better backfilling
- Upsert on backfill
- Change Sqlite -> Postgres
- Performance improvements on API and DB calls
- Fix assumptions, so we don't rely on them
- DbRepository interfaces
- Setup DB Migrations
- Tests
- Fix assumption of 1 block per slot
- Log colouring
- Handle reconnections:
  - Failures to connect to Node
  - Timeouts
  - Stream closed
