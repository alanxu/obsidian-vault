---
title: Design a Real-Time Voice Agent
slug: realtime-voice-agent
area: 3 — Agentic Systems (+ Area 2 serving)
companies: [OpenAI, "Sierra, Decagon (support)", "voice-AI startups", Robinhood]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[12-customer-support-agent]]", "[[06-llm-inference-serving-platform]]", "[[09-agent-platform]]"]
added: 2026-07-08 (audit fill — reported common 2026 prompt, e.g. "hospital voice assistant")
evidence: "GUIDE-LEVEL: 'Design a Hospital Voice Assistant (noise, privacy, latency, domain vocabulary)' cited as a common system-design question in 2026 AI-eng interview guides (aggregated, not company-attributed). OpenAI/Sierra/Decagon in companies = domain inference from their voice products."
---

# Design a Real-Time Voice Agent

> "A phone/voice assistant that converses naturally — support line, hospital scheduler, drive-thru." **Open with the number:** human turn-taking tolerance is **~500ms voice-to-voice**; a naive ASR→LLM→TTS chain is 2–4s. The whole design is **pipeline overlap + streaming everywhere + interruption handling**.

## Problem
"Design a hospital voice assistant" / "voice customer-support agent at 10K concurrent calls." Variants: with tool use (booking, lookup), multilingual, noisy environments, outbound calls.

## Clarify first
- Latency bar (conversational <1s vs IVR-replacement)? Concurrency scale? Telephony (8kHz, codecs) vs app audio?
- Tools/actions (world-changing → confirmation UX)? Privacy: HIPAA/PII — can audio leave region? Recording consent?
- Fallback to human — when and how (warm transfer with context)?

## Architecture
**Streaming pipeline, all stages overlapped:** audio in → **streaming ASR** (partial transcripts) → **endpointing/VAD** (semantic + silence: is the user done?) → LLM (streaming tokens, speculative "early start" on stable partials) → **streaming TTS** (sentence-chunked, starts on first sentence) → audio out. **Control plane:** dialog state, tool dispatcher (async — say "let me check" while tool runs), **barge-in handler** (user speaks → stop TTS, cancel in-flight generation, re-contextualize). **Platform:** session store, transcript log, safety filter on both directions, human-handoff bridge, per-call cost meter.

## Deep-dive — the latency budget (voice-to-voice ≤ ~800ms)
- ASR partials: continuous; final-segment ~100–200ms after speech end · endpointing decision: ~100–200ms (too eager = cuts users off; too lazy = dead air — tune per domain; semantic endpointing: LLM-ish "is this utterance complete?") · **LLM TTFT: 200–300ms** (small/distilled model or speculative decoding; prefix-cache the system prompt + dialog) · TTS first-audio: ~100–200ms streaming.
- **Overlap tricks:** start LLM prefill on partial transcript (discard if transcript changes); TTS speaks sentence 1 while sentence 2 generates; filler acknowledgments ("sure, one moment") mask tool latency ≥1s.
- **Barge-in is a hard cancel path:** detect user speech during TTS → stop audio <100ms, cancel LLM stream, mark spoken-so-far in dialog state (the model must know what the user actually *heard*).
- **Speech≠text pragmatics:** LLM output post-processed for speech (numbers, abbreviations, no markdown); disfluency-tolerant ASR + normalization; domain vocab (drug names) via biased/custom ASR lexicon.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Cascaded ASR→LLM→TTS vs end-to-end speech model | controllable/toolable/debuggable vs lower latency + prosody |
| Small fast model vs big smart model | latency vs capability (common: small responder + async big-model backup) |
| Eager vs lazy endpointing | interruptions vs dead air |
| On-region processing vs best cloud APIs | HIPAA/compliance vs quality |
| Filler speech vs silence during tools | perceived responsiveness vs feeling scripted |

## Numbers
Voice-to-voice target ≤800ms (great: 500ms; typical cascade unoptimized: 2–4s) · barge-in stop <100ms · telephony audio 8kHz mono (ASR quality hit vs 16kHz) · concurrency: each call = long-lived stateful session → session-affinity routing; 10K calls ≈ 10K concurrent streams (GPU pools sized on ASR+TTS+LLM per-stream cost).

## Eval
Turn latency p50/p95 (voice-to-voice, measured from user speech end) · task completion rate · barge-in handled correctly · WER on domain vocab · escalation rate + handoff quality · user talk-over/repeat-rate (proxy for latency + comprehension) · safety: no PII in logs, consent compliance.

## Failure modes
Endpointing cuts off slow speakers · barge-in race (agent talks over user) · ASR error on critical entity (dosage, account #) → **read-back confirmation for high-stakes slots** · tool latency → dead air → user hangs up · hallucinated policy answers (ground on KB → [[12-customer-support-agent]]) · cost blowup from long calls (cap + summarize dialog state).

## Top follow-ups
- "Where does the latency go and how do you cut it?" → budget table above; overlap + streaming + prefix cache + small model.
- "How do you handle interruptions?" → barge-in cancel path + dialog-state truth of what was heard.
- "Wrong transcription of a medication name?" → domain lexicon + confidence-gated read-back confirmation + human escalation.
- "End-to-end speech models (GPT-4o-audio style)?" → lower latency, better prosody; but tool use, grounding, and auditability are weaker — hybrid: e2e for chat, cascade for actions.
- "Scale to 10K calls?" → stateless pipeline workers + session store, GPU autoscale per stage, per-stage backpressure (degrade to "please hold" not drop).

## Related
[[12-customer-support-agent]] (the brain) · [[06-llm-inference-serving-platform]] (TTFT engineering) · [[09-agent-platform]] (tool runtime).
