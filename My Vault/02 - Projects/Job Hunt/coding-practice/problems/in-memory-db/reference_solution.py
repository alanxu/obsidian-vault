"""Reference solution — the 'append-only version list + binary search by ts' design.
Peek only after you've attempted solution.py. Verified by `python3 run.py in-memory-db --ref`.
"""
import bisect


class InMemoryDB:
    def __init__(self):
        self._d = {}      # key -> field -> list[(set_ts, value, expire_at|None)]  (sorted by set_ts)
        self._b = []      # list[(backup_ts, snapshot)]

    def _active(self, k, f, ts):
        v = self._d.get(k, {}).get(f)
        if not v:
            return None
        i = bisect.bisect_right([x[0] for x in v], ts) - 1
        if i < 0:
            return None
        _, val, exp = v[i]
        return None if (exp is not None and exp <= ts) else val

    def _put(self, k, f, val, ts, exp):
        self._d.setdefault(k, {}).setdefault(f, []).append((ts, val, exp))

    def _live(self, k, ts):
        return {f: self._active(k, f, ts)
                for f in self._d.get(k, {}) if self._active(k, f, ts) is not None}

    @staticmethod
    def _fmt(d):
        return ", ".join(f"{f}({d[f]})" for f in sorted(d))

    # ---- Level 1 ----
    def set(self, key, field, value):
        self._put(key, field, value, 0, None)

    def get(self, key, field):
        return self._active(key, field, 0) or ""

    def delete(self, key, field):
        if self._active(key, field, 0) is None:
            return "false"
        self._put(key, field, "", 0, 0)      # tombstone (expired immediately)
        return "true"

    # ---- Level 2 ----
    def scan(self, key):
        return self._fmt(self._live(key, 0))

    def scan_by_prefix(self, key, prefix):
        return self._fmt({f: v for f, v in self._live(key, 0).items() if f.startswith(prefix)})

    # ---- Level 3 ----
    def set_at(self, key, field, value, ts):
        self._put(key, field, value, ts, None)

    def set_at_with_ttl(self, key, field, value, ts, ttl):
        self._put(key, field, value, ts, ts + ttl)

    def get_at(self, key, field, ts):
        return self._active(key, field, ts) or ""

    def scan_at(self, key, ts):
        return self._fmt(self._live(key, ts))

    # ---- Level 4 ----
    def backup(self, ts):
        snap, n = {}, 0
        for k in self._d:
            live = {}
            for f in self._d[k]:
                val = self._active(k, f, ts)
                if val is None:
                    continue
                _, _, exp = self._d[k][f][bisect.bisect_right([x[0] for x in self._d[k][f]], ts) - 1]
                live[f] = (val, (exp - ts) if exp is not None else None)   # store REMAINING ttl
            if live:
                snap[k] = live
                n += 1
        self._b.append((ts, snap))
        return n

    def restore(self, ts, ts_to_restore):
        chosen = max((b for b in self._b if b[0] <= ts_to_restore), default=None, key=lambda b: b[0])
        if not chosen:
            return
        self._d = {}
        for k, fields in chosen[1].items():
            for f, (val, rem) in fields.items():
                self._put(k, f, val, ts, (ts + rem) if rem is not None else None)
