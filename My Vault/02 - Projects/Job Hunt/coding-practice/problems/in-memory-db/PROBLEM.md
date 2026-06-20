# In-Memory Key-Value Database (canonical CodeSignal ICA problem)

Implement `InMemoryDB` (in `solution.py`). Records are `key → {field: value}`. 90-min target; unlock each level by passing its tests. Run: `python3 run.py in-memory-db <level>`.

## Level 1 — basic CRUD
- `set(key, field, value)` — set a field's value.
- `get(key, field)` — return the value, or `""` if absent.
- `delete(key, field)` — return `"true"` if the field existed (and remove it), else `"false"`.

## Level 2 — scan / filter
- `scan(key)` — return `"f1(v1), f2(v2), …"` for all fields, **sorted by field name**.
- `scan_by_prefix(key, prefix)` — same, but only fields starting with `prefix`.

## Level 3 — timestamps + TTL
- `set_at(key, field, value, ts)`
- `set_at_with_ttl(key, field, value, ts, ttl)` — alive in the half-open window `[ts, ts+ttl)`.
- `get_at(key, field, ts)` — value active at `ts`, else `""`.
- `scan_at(key, ts)` — formatted live fields at `ts`.

## Level 4 — backup / restore
- `backup(ts)` — snapshot live records, **preserving each field's remaining TTL**; return the count of non-empty records.
- `restore(ts, ts_to_restore)` — restore from the latest backup taken at or before `ts_to_restore`; TTLs resume relative to `ts`.

> Design tip: store an **append-only version list per (key, field)** of `(set_ts, value, expire_at)` and binary-search by timestamp — that one structure serves all 4 levels. Reference in `reference_solution.py` (peek only after you try).
