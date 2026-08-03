---
title: The Core Loop
pillar: harness
parent: ./README.md
section: "3.1"
---

# 3.1 The Core Loop

Every agent is a state machine. Make it explicit:

```python
state = {goal, history, scratchpad, tools, budget}
while not done(state):
    decision = llm.decide(state)        # may be: tool_call | final | replan
    state = apply(state, decision)
    state = enforce_invariants(state)   # budget, loops, safety
return state.result
```

**Hard rules live in the loop, not the prompt:**

- Max steps (e.g. 25)
- Max tokens / cost per run
- Max wall time
- Loop detection (same tool call 3x → break)
- Schema validation before tool execution
