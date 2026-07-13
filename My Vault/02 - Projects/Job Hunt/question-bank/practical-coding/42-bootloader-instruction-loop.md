---
title: Bootloader — Instruction VM, Loop Detection & One-Swap Repair
slug: bootloader-instruction-loop
type: live-coding (progressive)
leetcode: null
companies: [Anthropic (reported phone screen), "general"]
difficulty: ★★★☆☆
frequency: medium (Anthropic phone screen)
formats: [Live, OA·GCA/HR]
levels: 4
time-box: live 30–45 min
tags: [interpreter, virtual-machine, cycle-detection, visited-set, graph-reachability, refactor]
related: ["[[13-stack-trace-to-trace-conversion]]", "[[14-exclusive-execution-time]]", "[[09-cd-directory-navigation]]"]
source: "1point3acres — Anthropic SWE phone-screen report 'Bootloader Problem' (thread 1178806, login-gated; corroborated by the public summary). Structure = classic 'Handheld Halting' instruction VM. Digested 2026-07-13."
---

# Bootloader — Instruction VM, Loop Detection & One-Swap Repair

> **Reported Anthropic phone technical screen ("Bootloader problem").** A tiny virtual machine that boots by running a list of instructions. It's graded like the rest of Anthropic's bank: **can you build a clean interpreter, then extend it** as requirements pile on (detect the infinite loop → repair the program → repair it efficiently). Practical, not a trick — the muscle is *cycle detection on execution* plus a *graph-reachability* insight at the end.

## Problem
A boot program is a list of instructions, one per line. Each is an **operation** and a **signed integer argument**:

- `acc N` — add `N` to a global **accumulator**, then advance to the next instruction (`ip += 1`).
- `jmp N` — jump: `ip += N` (relative; `N` may be negative).
- `nop N` — no operation; ignore `N` and advance (`ip += 1`).

Execution starts with `accumulator = 0` at `ip = 0`. The program **terminates** when `ip` moves exactly **one past the last instruction** (`ip == len(program)`).

> **Clarify first:** Is termination strictly `ip == len` (falling off the bottom), and is any other out-of-range `ip` (`<0` or `>len`) a *crash* vs. termination? Can the same instruction legally run twice (→ loop) or is that always a bug? Is exactly **one** instruction corrupted in the repair part, and is it always a `jmp`↔`nop` swap (never `acc`)? Are we returning the **accumulator**, the **swapped index**, or both?

## The interview arc (levels)
- **L1 — build the VM.** Parse the lines; run the program assuming it terminates; return the accumulator. Clean dispatch on `acc`/`jmp`/`nop`.
- **L2 — detect the infinite loop.** The boot program revisits an instruction and loops forever. Run until an instruction is **about to execute a second time**; stop and return `(accumulator_so_far, looped=True)`. A **visited-set of instruction pointers** is the whole trick — O(n) time, O(n) space.
- **L3 — repair it (one-swap fix).** Exactly one `jmp`↔`nop` is corrupted. Find the single flip that makes the program **terminate**, and return the terminating accumulator (and the swapped index). Brute force: try flipping each `jmp`/`nop`, simulate, keep the one that halts — O(n²).
- **L4 — repair in O(n).** Don't re-simulate per candidate. Using reachability (forward from start + backward from the end), find a valid swap in linear time; handle *no valid fix*, dead/unreachable code, and multiple corruptions.

## Core approach — one interpreter, reused every level
Model each instruction as `(op, arg)`. The executor is a loop over `ip` with a **visited set** so it always halts (either real termination or a detected cycle). Everything else is built on top of this one function.

```python
from typing import List, Tuple, Optional

Program = List[Tuple[str, int]]

def parse(lines: List[str]) -> Program:
    prog = []
    for line in lines:
        op, arg = line.split()
        prog.append((op, int(arg)))          # arg like "+3" / "-4" -> int() handles the sign
    return prog

def run(prog: Program) -> Tuple[int, bool]:
    """Execute until termination or a repeated instruction.

    Returns (accumulator, terminated):
      terminated=True  -> ip fell off the end (ip == len): accumulator is final.
      terminated=False -> a loop was detected: accumulator is the value *just before*
                          the first instruction would run a second time.
    """
    acc, ip, seen = 0, 0, set()
    while ip != len(prog):
        if ip in seen:                        # about to repeat -> infinite loop
            return acc, False
        if not (0 <= ip < len(prog)):         # out-of-range jump -> crash (treat as non-terminating)
            return acc, False
        seen.add(ip)
        op, arg = prog[ip]
        if op == "acc":
            acc += arg; ip += 1
        elif op == "jmp":
            ip += arg
        else:                                  # nop
            ip += 1
    return acc, True                           # ip == len -> clean termination
```

- **L1** = `run(prog)[0]` on a program known to terminate.
- **L2** = `run(prog)` — the `terminated=False` branch returns the pre-loop accumulator.

### L3 — one-swap repair (brute force, O(n²))
```python
def repair(prog: Program) -> Optional[Tuple[int, int]]:
    """Flip exactly one jmp<->nop so the program terminates.

    Returns (accumulator_at_termination, swapped_index), or None if no single
    swap fixes it. 'acc' instructions are never candidates.
    """
    flip = {"jmp": "nop", "nop": "jmp"}
    for i, (op, arg) in enumerate(prog):
        if op == "acc":
            continue
        patched = prog[:i] + [(flip[op], arg)] + prog[i + 1:]
        acc, terminated = run(patched)
        if terminated:
            return acc, i
    return None
```
**Complexity:** each candidate re-runs the VM → **O(n²)** time. Fine for phone-screen sizes; L4 is the "make it linear" ask.

## L4 — linear-time repair (the senior insight)
Re-simulating per candidate is wasteful. Two linear passes replace it:

1. **Forward-reachable set** `R`: instruction pointers reachable from `ip=0` *before* the loop (the visited set from a single normal run).
2. **Can-terminate set** `C`: pointers from which execution *would* reach `ip == len` **if no further swap happens**. Build it by walking the **reverse graph** from the terminal position: an index `i` is in `C` if its natural successor is in `C` (`nop`/`acc` → `i+1`; `jmp` → `i+arg`). Seed with `len(prog)` (termination).

A single swap fixes the program iff there is a **reachable** index `i ∈ R` whose **flipped** successor lands in `C`:
- flip a `nop N` at `i` → it becomes `jmp N` → succeeds iff `i + N ∈ C`;
- flip a `jmp N` at `i` → it becomes `nop`  → succeeds iff `i + 1 ∈ C`.

Scan `R` once, test the flipped edge against `C`, and you've found the swap in **O(n)** time / space — no re-simulation. (Then one more `run` on the patched program yields the accumulator, still O(n).)

> **Why this is the "staff" answer:** it reframes an execution-simulation problem as **graph reachability** (forward cone ∩ backward cone), which also generalizes to "*is there any k-swap fix?*" and to reporting **all** valid single swaps.

## Edge cases to name out loud
- **Already terminates** with no swap → repair should report "no swap needed" (or return the natural run), not force a flip.
- **No valid single swap exists** → return a sentinel (`None`), don't loop forever — the `run` visited-set guarantees every candidate halts.
- **`acc` is never a candidate** — flipping it isn't allowed; only `jmp`↔`nop`.
- **Negative / large jumps** landing `ip < 0` or `ip > len` → decide crash vs. terminate; only `ip == len` is clean termination.
- **Dead/unreachable code** — instructions never in `R` can't be the fix; the linear method skips them for free.
- **Self-loop** `jmp +0` → caught by the visited-set on the very next step.

## By format
### Live · CoderPad — *primary (Anthropic phone screen)*
- **Follow-ups (the realistic pile-on):**
  1. "It never finishes — why, and what do you return?" → visited-set loop detection (L2).
  2. "One instruction is wrong; fix it." → one-swap repair (L3).
  3. "Program is huge — don't brute-force it." → the O(n) reachability method (L4).
  4. "Report *which* line to change" / "report *all* valid fixes." → return indices; collect every `i ∈ R` with flipped edge in `C`.
  5. "Support two corruptions" / "an `acc` could also be corrupted." → generalizes the cone intersection; discuss the blow-up.
  6. "Stream the program / it doesn't fit in memory." → you still need random access for `jmp`; discuss why an index is required.
- **Tips:** build `run` **once** and reuse it verbatim for L1/L2/L3 — resist rewriting per level (that's exactly the "extend without breaking" signal Anthropic grades). Narrate the visited-set as your termination guarantee. For L4, *draw* the forward cone and backward cone before coding.
- **Pitfalls:** treating any out-of-range `ip` as termination (only `ip == len` is); mutating the shared program in place while brute-forcing (copy or restore); forgetting to reset `acc`/`ip`/`seen` between candidate runs; off-by-one on the `jmp` target; flipping `acc`.

### OA · GCA / HR (auto-graded)
- **Tips:** L1+L2 (run + loop-detect) pass most graders; keep the dispatch tight and integer-parse the signed arg with `int()`.
- **Pitfalls:** off-by-one on termination (`ip == len`, not `ip == len-1`); not deep-copying per candidate in the repair.

## Company variants
- **Anthropic (reported)** — "bootloader" framing: run it, detect the loop, then **swap one instruction to avoid the loop**. Exactly the L2→L3 arc; strong candidates volunteer L4.
- **Generic "Handheld Halting"** — identical VM under a different story (game console boot code). Same `acc/jmp/nop` set.
- **Instruction-set reskins** — add `mul`/`out`/`set` ops or registers; the interpreter loop + visited-set structure is unchanged (see [[14-exclusive-execution-time]] for another "execute a program, track state" cousin).

## Worked example trace
```
program (index: op arg):
  0: nop +0
  1: acc +1
  2: jmp +4
  3: acc +3
  4: jmp -3
  5: acc -99
  6: acc +1
  7: jmp -4
  8: acc +6

L2 (loop detect):
  ip0 nop -> ip1
  ip1 acc+1 (acc=1) -> ip2
  ip2 jmp+4 -> ip6
  ip6 acc+1 (acc=2) -> ip7
  ip7 jmp-4 -> ip3
  ip3 acc+3 (acc=5) -> ip4
  ip4 jmp-3 -> ip1   # ip1 already in seen -> LOOP
  => run() returns (5, False)          # accumulator just before the repeat = 5

L3 (one-swap repair): flip index 7  jmp -4 -> nop -4
  ... ip6 acc+1 (acc=2) -> ip7 nop -> ip8 acc+6 (acc=8) -> ip9 == len  # TERMINATES
  => repair() returns (8, 7)           # accumulator=8, swapped line 7
```

## Related
[[13-stack-trace-to-trace-conversion]] (another Anthropic parse-and-simulate) · [[14-exclusive-execution-time]] (execute a program, track state on a stack) · [[09-cd-directory-navigation]] (small interpreter over a command list) · runnable code → `interview-questions/practical-coding/42-bootloader-instruction-loop/`.
