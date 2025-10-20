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
- Fix ordering for Blocks and Transactions
- Fix assumption of 1 block per slot
- Split the single file static into components
- Log colouring

- Store hashes
- Get transaction by hash
- Get block by hash
