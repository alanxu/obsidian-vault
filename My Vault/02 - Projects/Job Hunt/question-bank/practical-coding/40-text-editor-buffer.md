---
title: Text Editor Buffer (insert/delete/read + undo/redo)
slug: text-editor-buffer
type: stateful-service
leetcode: "2296 (design a text editor) — cursor variant"
companies: [Anysphere, "editor/IDE teams", OpenAI, general]
difficulty: ★★★☆☆
frequency: medium (high at Anysphere/Cursor)
formats: [Live, Onsite·NR]
levels: 3
time-box: live 40–50 min
tags: [editor, buffer, undo-redo, command-pattern, rope, gap-buffer, piece-table]
related: ["[[21-in-memory-file-system]]", "[[29-range-module]]", "[[practical-oo-coding-deep-guide]]"]
added: 2026-07-08 (audit fill — Cursor reported: editor buffer with efficient ops; rope/concurrent-edit follow-ups)
evidence: "VERIFIED: Cursor guides (jobsbyculture, codemia 2026) report 'design a text-editor buffer with efficient insert/delete/read; discuss ropes and concurrent edits' as an interview question. OpenAI/general = inference (LC 2296 exists broadly)."
---

# Text Editor Buffer

Cursor-reported: "design a data structure for a text editor buffer supporting efficient insert, delete, and read," escalating to undo/redo and concurrent edits. The live-coding expectation is a **clean API + command-pattern undo/redo**; the *discussion* expectation is knowing why real editors use **gap buffers / piece tables / ropes** instead of one Python string.

## Problem

```python
ed.insert(pos: int, text: str)
ed.delete(pos: int, length: int) -> str    # returns deleted text (you'll need it for undo)
ed.read(pos: int, length: int) -> str
# L2:
ed.undo(); ed.redo()                        # new edit clears the redo stack
# L3 (usually discussion): cursor ops, concurrent editors, large-file complexity
```

## Core approach (format-agnostic)

Code the command pattern over a simple backing store; **name** the better stores and their complexities.

```python
class TextEditor:
    def __init__(self, text=""):
        self.buf = list(text)            # list[str] beats str (no full copy per edit)
        self.undo_stack, self.redo_stack = [], []

    def insert(self, pos, text):
        pos = max(0, min(pos, len(self.buf)))
        self.buf[pos:pos] = list(text)
        self.undo_stack.append(("delete", pos, len(text)))
        self.redo_stack.clear()          # new edit invalidates redo branch

    def delete(self, pos, length):
        pos = max(0, min(pos, len(self.buf)))
        removed = "".join(self.buf[pos:pos+length])
        del self.buf[pos:pos+length]
        self.undo_stack.append(("insert", pos, removed))
        self.redo_stack.clear()
        return removed

    def read(self, pos, length):
        return "".join(self.buf[pos:pos+length])

    def undo(self):
        self._apply(self.undo_stack, self.redo_stack)

    def redo(self):
        self._apply(self.redo_stack, self.undo_stack)

    def _apply(self, src, dst):
        if not src: return
        op, pos, arg = src.pop()
        if op == "insert":
            self.buf[pos:pos] = list(arg)
            dst.append(("delete", pos, len(arg)))
        else:                            # delete
            removed = "".join(self.buf[pos:pos+arg])
            del self.buf[pos:pos+arg]
            dst.append(("insert", pos, removed))
```

**Key insight to narrate:** the undo entry is the **inverse operation** (delete stores the removed text; insert stores the length), and undo/redo are symmetric — `_apply` moving inverses between stacks means redo needs no special casing. New edits clear redo (linear history; version-tree is the follow-up).

**Complexity.** list backing: insert/delete O(n), read O(k). The escalation table (recite, don't implement):

| Structure | insert/delete | read range | notes |
|---|---|---|---|
| string | O(n) + full copy | O(k) | fine for interviews only |
| **gap buffer** | O(1) amortized *at cursor*, O(n) to move gap | O(k) | Emacs; brilliant for localized typing |
| **piece table** | O(#pieces) | O(#pieces) | VS Code; original+append-only buffers, edits are piece splits — undo is nearly free (keep old piece list) |
| **rope** (balanced tree of chunks) | O(log n) | O(log n + k) | huge files; structural sharing → cheap snapshots |

## By format

### Live · CoderPad — *primary*
- **How it appears:** L1 API (~15 min) → undo/redo (~15 min) → "how would this scale to a 2GB file / multiple cursors?" (discussion).
- **Follow-ups (reported/likely):**
  - **Undo/redo semantics** — redo cleared on new edit? (yes, linear); grouping keystrokes into one undo unit (flush on pause/word boundary — batch commands).
  - **Rope/piece-table discussion** — why O(n) list fails at 100MB; piece table's append-only buffers make undo/versioning natural.
  - **Cursor-relative API** (LC 2296) — `addText/deleteText/moveCursor` → gap buffer *is* the cursor; or two stacks (left/right of cursor) — elegant and O(1) per op.
  - **Concurrent edits** (Cursor's actual business) — two editors at different positions: positions shift → **operational transform** (rebase op B's position past op A) vs **CRDT** (position = stable IDs not integers); know the two names + one sentence each.
  - **Persistence** — save = snapshot vs op-log replay; op-log gives you undo-across-sessions and time-travel.
  - **Search over the buffer** — line index (offsets of `\n`) maintained incrementally for O(1) line lookup.
- **Tips:**
  - `list[str]` not `str` — narrate why (immutability → O(n) copy per keystroke).
  - Clamp positions defensively; interviewers throw `pos > len` early.
  - State the inverse-op invariant before coding undo — it *is* the design.
  - Multi-op trace: insert, delete, undo, undo, redo, insert (redo now dead) — walk it aloud.
- **Pitfalls:**
  - Forgetting to clear redo on new edit → time-travel corruption.
  - Undo of delete without having *saved the deleted text* — the reason `delete` returns it.
  - Storing full-buffer snapshots per op → O(n) memory per keystroke (fine to *mention* as snapshot+diff hybrid).
  - Off-by-one at `pos == len(buf)` (append case).
  - Claiming rope is O(1) — it's O(log n); precision counts at editor companies.

### Onsite · NR
- Write the command-pattern core by hand; trace the 6-op sequence above; draw the piece table for one insert into "HELLO" and show why undo = restore old piece list.

## Worked example trace

```
insert(0,"hello world") → buf="hello world", undo=[(del,0,11)]
delete(5,6)  → removed=" world", buf="hello", undo=[...,(ins,5," world")]
undo()       → re-insert " world" @5 → buf="hello world", redo=[(del,5,6)]
redo()       → delete 6 @5 → buf="hello", redo=[]
insert(5,"!")→ buf="hello!", redo cleared ✓
```

## Cross-track map
- **B** = this card · **Cursor loop** = pair with [[37-streaming-json-parser]] (streaming edits) and their context-retrieval design ([[../llm-system-design/07-code-completion-serving-sub100ms]]).

## Related
[[21-in-memory-file-system]] (state + paths) · [[29-range-module]] (interval bookkeeping sibling) · [[37-streaming-json-parser]] (Cursor loop companion).
