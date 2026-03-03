# /workspace/dllm/CONTEXT_REFRESH.md

## Purpose
This file refreshes long-horizon project context after a full documentation and repository pass so future implementation work can proceed with fewer blind spots.

## Repository mission and operating model
- `/workspace/dllm` is a unified research/engineering codebase for diffusion language model training, sampling, and evaluation.
- Design pattern: reusable primitives in `/workspace/dllm/dllm/core`, model/pipeline specialization in `/workspace/dllm/dllm/pipelines`, and runnable entry points in `/workspace/dllm/examples`.
- Current workstream priority is the additive omnimodal subsystem under `/workspace/dllm/dllm/omnimodal`, intended to preserve text-only backward compatibility while enabling mixed-modality ingestion and training hooks.

## Current status snapshot (from planning docs)
- `/workspace/dllm/TASKS.md` shows Phases 0-7 marked done and Phase 8 (hardening/validation sweep) in progress.
- `/workspace/dllm/TODOs.md` indicates remaining actionable work:
  - weighted modality/source sampling + curriculum hooks,
  - broad compatibility sweeps,
  - final rollback-safety checklist execution,
  - concrete backend integrations for image/video/audio/pdf tokenization.
- `/workspace/dllm/IMPLEMENTATION_SUMMARY.md` confirms implementation is intentionally split between production-ready text/MIDI + ingestion/collation components and stubbed media tokenization backends.

## Architecture view for next contributors

### Stable baseline surfaces
- Training/evaluation core abstractions:
  - `/workspace/dllm/dllm/core/trainers`
  - `/workspace/dllm/dllm/core/samplers`
  - `/workspace/dllm/dllm/core/eval`
- Utility and data helpers:
  - `/workspace/dllm/dllm/utils`
  - `/workspace/dllm/dllm/data`

### Omnimodal extension surfaces
- Contracts and config:
  - `/workspace/dllm/dllm/omnimodal/contracts.py`
  - `/workspace/dllm/dllm/omnimodal/config.py`
- Data route and parsing:
  - `/workspace/dllm/dllm/omnimodal/detection.py`
  - `/workspace/dllm/dllm/omnimodal/ingestion.py`
  - `/workspace/dllm/dllm/omnimodal/manifest.py`
- Learning path integration:
  - `/workspace/dllm/dllm/omnimodal/adapters.py`
  - `/workspace/dllm/dllm/omnimodal/collators.py`
  - `/workspace/dllm/dllm/omnimodal/strategies.py`
  - `/workspace/dllm/dllm/omnimodal/trainer_hooks.py`
  - `/workspace/dllm/dllm/omnimodal/sampler.py`

### Validation assets
- Unit tests for omnimodal components are concentrated in `/workspace/dllm/scripts/tests/test_omnimodal_*.py`.
- Example docs and scripts for usage and schema checks:
  - `/workspace/dllm/docs/omnimodal.md`
  - `/workspace/dllm/examples/omnimodal/README.md`
  - `/workspace/dllm/examples/omnimodal/validate_manifest.py`

## High-confidence next execution plan
1. Complete Phase 8 hardening by running full test coverage in `/workspace/dllm/scripts/tests` and documenting any flaky tests with deterministic repro commands.
2. Implement weighted modality/source sampling and curriculum hook scaffolding behind explicit feature flags in omnimodal config.
3. Land first concrete non-text backend (image or audio) via adapter registry to reduce stub surface area.
4. Wire optional omnimodal hooks into one pipeline entry script in `/workspace/dllm/examples` with default-off behavior.
5. Add explicit backward-compatibility evidence for text-only paths in CI notes and docs.

## Guardrails for future changes
- Preserve additive, opt-in semantics: avoid modifying existing text paths unless explicitly enabled by config.
- Keep failure semantics actionable: backend gaps should raise clear errors rather than silent degradation.
- Maintain deterministic data path behavior (ordering, policy traces, and seeded randomness).
- Prefer incremental integration (single backend + tests + docs) over broad simultaneous rewrites.
