"""Your solution. Fill each method, then run:  python3 run.py in-memory-db <level>

Stub raises NotImplementedError so unrun levels fail clearly.
See PROBLEM.md for the spec; reference_solution.py for a worked answer (peek only after you try).
"""


class InMemoryDB:
    def __init__(self):
        raise NotImplementedError

    # ---- Level 1 ----
    def set(self, key, field, value):
        raise NotImplementedError

    def get(self, key, field):
        raise NotImplementedError

    def delete(self, key, field):
        raise NotImplementedError

    # ---- Level 2 ----
    def scan(self, key):
        raise NotImplementedError

    def scan_by_prefix(self, key, prefix):
        raise NotImplementedError

    # ---- Level 3 ----
    def set_at(self, key, field, value, ts):
        raise NotImplementedError

    def set_at_with_ttl(self, key, field, value, ts, ttl):
        raise NotImplementedError

    def get_at(self, key, field, ts):
        raise NotImplementedError

    def scan_at(self, key, ts):
        raise NotImplementedError

    # ---- Level 4 ----
    def backup(self, ts):
        raise NotImplementedError

    def restore(self, ts, ts_to_restore):
        raise NotImplementedError
