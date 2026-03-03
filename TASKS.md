# /workspace/dllm/TASKS.md

## Architecture Audit Summary (Step 1)

### Current repository shape
- Core trainer/sampler abstractions live under `/workspace/dllm/dllm/core/*` and are thinly specialized over `transformers.Trainer` plus diffusion-specific schedulers.
- Data loading today is text-centric and mostly routed through `/workspace/dllm/dllm/data/utils.py` plus helper tokenization functions in `/workspace/dllm/dllm/utils/data.py`.
- Pipeline-level specializations are isolated in `/workspace/dllm/dllm/pipelines/*` and examples in `/workspace/dllm/examples/*`.
- Tests are pytest-based and live in `/workspace/dllm/scripts/tests` with compact unit tests and clear fixture-level expectations.

### Style and reliability conventions identified
- Dataclass-heavy config pattern (`ModelArguments`, `DataArguments`, trainer config subclasses).
- Logging pattern via `dllm.utils.utils.get_default_logger`.
- Explicit deterministic behavior where possible (e.g., split truncation helpers, seed usage in args).
- Optional behavior switches are usually explicit flags, not hidden auto-magic.
- New tests should follow existing path `/workspace/dllm/scripts/tests/test_*.py`.

### Extension points selected
1. New modality subsystem under `/workspace/dllm/dllm/omnimodal` to avoid destabilizing existing text-only paths.
2. Optional trainer mixin/hooks in `/workspace/dllm/dllm/core/trainers` to preserve backward compatibility.
3. Reusable collator components in `/workspace/dllm/dllm/utils/collators.py` style, but scoped to omnimodal package.
4. New docs/examples under `/workspace/dllm/docs` and `/workspace/dllm/examples/omnimodal`.

---

## Phase plan and status board

| Phase | Goal | Status |
|---|---|---|
| Phase 0 | Audit / design / contracts | done |
| Phase 1 | Ingestion + modality detection | done |
| Phase 2 | Tokenization abstraction interfaces | done |
| Phase 3 | Dataset manifest + labeled/unlabeled handling | done |
| Phase 4 | Mixed-batch collators + loaders | done |
| Phase 5 | Trainer integration hooks | done |
| Phase 6 | Sampler/inference hooks (MVP) | done |
| Phase 7 | Examples + docs + tests | done |
| Phase 8 | Hardening / edge cases / validation sweep | done |

---

## Detailed task decomposition

### Phase 0 — Audit / design / contracts

#### P0-T01: Create omnimodal architecture contract docs
- **Status**: done
- **Inputs**: existing trainers/data utils/tests.
- **Outputs**: this task plan + design notes.
- **Depends on**: none.
- **Can run in parallel with**: P0-T02.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - Documented plugin-first architecture.
  - Compatibility constraints explicitly listed.
- **Validation**:
  - `cat /workspace/dllm/TASKS.md`
- **Rollback plan**: remove only planning docs.

#### P0-T02: Define strict schema contracts before implementation
- **Status**: done
- **Inputs**: requirements for manifest/token packages/strategies.
- **Outputs**: typed dataclasses/protocols in new module.
- **Depends on**: P0-T01.
- **Can run in parallel with**: none (contract baseline).
- **Breakage risk**: low.
- **Acceptance criteria**:
  - Contracts compile and are importable.
  - Include feature flags/stub semantics.
- **Validation**:
  - `python -c "import dllm.omnimodal"`
- **Rollback plan**: revert new package only.

### Phase 1 — Ingestion + modality detection

#### P1-T01: Implement modality enum, extension map, MIME/sniff probes
- **Status**: done
- **Inputs**: file suffix policies.
- **Outputs**: deterministic router + policy config.
- **Depends on**: P0-T02.
- **Can run in parallel with**: P1-T02.
- **Breakage risk**: low (isolated module).
- **Acceptance criteria**:
  - Supports txt/md/pdf/jpg/jpeg/png/webp/gif/mp4/avi/webm/mp3/wav/flac/mid/midi.
  - GIF policy: image/video adaptive.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_detection.py -v`
- **Rollback plan**: remove detection module.

#### P1-T02: Build folder scanner + skip/retry/quarantine ledger
- **Status**: done
- **Inputs**: root dir + recursive flags + ignore patterns.
- **Outputs**: lazy sample iterator + dropped-sample manifest writer.
- **Depends on**: P1-T01.
- **Can run in parallel with**: P2-T01 (contracts only).
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - Deterministic ordering + seeded shuffling.
  - Bad samples logged with reason and timestamp.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_ingestion.py -v`
- **Rollback plan**: disable via config feature flag.

### Phase 2 — Tokenization abstraction

#### P2-T01: TokenizationAdapter contract + registry
- **Status**: done
- **Inputs**: modality route outputs.
- **Outputs**: adapter protocol/ABC + registry + capability flags.
- **Depends on**: P0-T02.
- **Can run in parallel with**: P1-T02.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - can_handle/encode/decode/batch_encode available.
  - clear stub error path.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_adapters.py -v`
- **Rollback plan**: keep only text adapter + null registry.

#### P2-T02: Initial adapters (text functional; others stub/hook; MIDI minimal)
- **Status**: done
- **Inputs**: adapter contract.
- **Outputs**: text/image/video/audio/midi/pdf adapters.
- **Depends on**: P2-T01, P1-T01.
- **Can run in parallel with**: P3-T01.
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - Text adapter wraps existing tokenizer path.
  - non-configured backends raise actionable error.
  - MIDI event tokenizer minimally functional.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_adapters.py -v`
- **Rollback plan**: disable non-text adapters via feature flags.

### Phase 3 — Manifest schema + labeled/unlabeled

#### P3-T01: Manifest dataclass schema + JSONL parser/validator
- **Status**: done
- **Inputs**: dataset requirements.
- **Outputs**: schema with labels/metadata/grouping/provenance/confidence.
- **Depends on**: P0-T02.
- **Can run in parallel with**: P2-T02.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - unlabeled + weak + labeled represented uniformly.
  - validation errors include field path.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_manifest.py -v`
- **Rollback plan**: parser fallback to permissive mode.

#### P3-T02: PDF adaptive decomposition policy
- **Status**: done
- **Inputs**: pdf handling modes.
- **Outputs**: auto/text-only/image-only/hybrid route behavior.
- **Depends on**: P1-T01, P2-T02.
- **Can run in parallel with**: P4-T01.
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - emits deterministic decomposed sub-samples with temporal/page metadata.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_pdf.py -v`
- **Rollback plan**: force `text-only` mode.

### Phase 4 — Mixed-batch collators + loaders

#### P4-T01: Unified token package schema and batch collator
- **Status**: done
- **Inputs**: adapter outputs.
- **Outputs**: modality IDs, boundaries, masks, sidecar metadata.
- **Depends on**: P2-T01, P3-T01.
- **Can run in parallel with**: P5-T01.
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - no modality-specific if/else explosion in trainer-facing batch.
  - max token budget batching supported.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_collator.py -v`
- **Rollback plan**: fallback to single-modality batches.

#### P4-T02: Adaptive objective strategy registry
- **Status**: done
- **Inputs**: token package + manifest labels.
- **Outputs**: deterministic objective selection and mask generation.
- **Depends on**: P4-T01.
- **Can run in parallel with**: P6-T01.
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - supports labeled/unlabeled strategies + failure behavior contract.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_strategies.py -v`
- **Rollback plan**: default to masked denoising strategy only.

### Phase 5 — Trainer integration hooks

#### P5-T01: Non-breaking trainer mixin for modality-aware preprocessing/loss aggregation
- **Status**: done
- **Inputs**: current trainers and token package format.
- **Outputs**: optional hook class preserving text-only behavior.
- **Depends on**: P4-T01.
- **Can run in parallel with**: docs tasks.
- **Breakage risk**: high (trainer internals).
- **Acceptance criteria**:
  - existing text scripts run unchanged.
  - per-modality/objective metrics emitted when enabled.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_trainer_hooks.py -v`
- **Rollback plan**: disable hooks by default.

### Phase 6 — Sampler/inference hooks (MVP)

#### P6-T01: Minimal modality-aware sampler entrypoint
- **Status**: done
- **Inputs**: token package schema + adapter decode capability flags.
- **Outputs**: inference routing with graceful NotImplemented decode handling.
- **Depends on**: P2-T01, P4-T01.
- **Can run in parallel with**: P7 tasks.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - text decode works; unsupported decode paths error clearly.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_sampler.py -v`
- **Rollback plan**: keep sampler under experimental namespace.

### Phase 7 — Docs, examples, tests

#### P7-T01: Add examples/configs/manifests for mixed data
- **Status**: done
- **Inputs**: previous phases.
- **Outputs**: runnable examples for text-only and mixed modes.
- **Depends on**: P1-P6 core tasks.
- **Can run in parallel with**: P7-T02.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - includes labeled/unlabeled hybrid manifest example.
- **Validation**:
  - `python /workspace/dllm/examples/omnimodal/validate_manifest.py --help`
- **Rollback plan**: retain docs-only examples.

#### P7-T02: Add comprehensive test suite for all new modules
- **Status**: done
- **Inputs**: all implementations.
- **Outputs**: deterministic unit tests with tiny fixtures.
- **Depends on**: P1-P6.
- **Can run in parallel with**: P7-T01.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - corrupt-file and missing-backend behavior covered.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests/test_omnimodal_* -v`
- **Rollback plan**: keep smoke-only tests if CI timeouts.

### Phase 8 — Hardening and final validation

#### P8-T01: End-to-end smoke and compatibility sweep
- **Status**: done
- **Inputs**: full branch.
- **Outputs**: validated status notes and known gaps.
- **Depends on**: all prior tasks.
- **Can run in parallel with**: none.
- **Breakage risk**: medium.
- **Acceptance criteria**:
  - text-only compatibility proven.
  - mixed ingestion + graceful stubs proven.
- **Validation**:
  - `pytest /workspace/dllm/scripts/tests -v`
- **Rollback plan**: revert latest phase-specific commits selectively.


#### P8-T02: Finalize GIF adaptive frame-threshold policy
- **Status**: done
- **Inputs**: open GIF policy blocker from `/workspace/dllm/TODOs.md`.
- **Outputs**: configurable `gif_video_frame_threshold` with config validation and ingestion wiring.
- **Depends on**: P1-T01.
- **Can run in parallel with**: none.
- **Breakage risk**: low.
- **Acceptance criteria**:
  - Adaptive GIF routing threshold is explicit and deterministic.
  - Non-positive threshold values fail fast during config validation.
- **Validation**:
  - `PYTHONPATH=/workspace/dllm pytest /workspace/dllm/scripts/tests/test_omnimodal_detection.py /workspace/dllm/scripts/tests/test_omnimodal_scheduling.py -v`
- **Rollback plan**: revert threshold field and return to fixed threshold semantics.

---

## Risk register

1. **Optional media dependencies unavailable in runtime**
   - Mitigation: lazy imports + actionable stub errors + feature flags.
2. **Trainer API coupling creates regressions**
   - Mitigation: hook mixins default-off; preserve original call paths.
3. **PDF/GIF ambiguity causes inconsistent routing**
   - Mitigation: deterministic policy config + explicit metadata trace.
4. **Large-file ingestion instability**
   - Mitigation: lazy iterators, skip/retry policy, quarantine manifest.

## Open questions and assumptions

- Assumption: Existing training loops remain text-first; omnimodal support enters via new optional dataset/collator path.
- Assumption: Minimal MIDI tokenizer is acceptable as event parser with deterministic token IDs.
- Open question: Preferred external backend list for image/video/audio tokenizers (left as pluggable stubs).

## Compatibility notes
- Existing text workflows should remain unchanged by default (`omnimodal.enabled=False`).
- New modules are additive and behind opt-in configs.

## Progress notes (validation journal)
- [done] Created planning scaffolding and phase decomposition.
- [done] Implementation completed with tests and smoke checks recorded in final validation section.

## Post-PhD engineering reference snippets

```text
Pattern: "Define contracts before integration"
- Establish schema/versioned dataclasses first.
- Ensure adapters and trainers consume only contracts.
- Enforce compatibility with explicit capability flags.
```

```text
Pattern: "Failure is data"
- Persist dropped samples and route failures to quarantine JSONL.
- Never silently swallow parser/tokenizer errors.
- Keep reasons machine-readable for automated triage.
```

```text
Pattern: "Determinism gates"
- Sort before shuffle.
- Seed all randomization points explicitly.
- Encode policy decisions into metadata for replayability.
```

## Final validation evidence
- `PYTHONPATH=/workspace/dllm pytest /workspace/dllm/scripts/tests/test_omnimodal_detection.py /workspace/dllm/scripts/tests/test_omnimodal_manifest.py /workspace/dllm/scripts/tests/test_omnimodal_adapters.py /workspace/dllm/scripts/tests/test_omnimodal_collator.py /workspace/dllm/scripts/tests/test_omnimodal_ingestion.py -v` ✅
- `PYTHONPATH=/workspace/dllm python /workspace/dllm/examples/omnimodal/validate_manifest.py --manifest /workspace/dllm/examples/omnimodal/sample_manifest.jsonl` ✅
- `PYTHONPATH=/workspace/dllm pytest /workspace/dllm/scripts/tests/test_data_utils.py -v` ✅
- `PYTHONPATH=/workspace/dllm python -m compileall /workspace/dllm/dllm/omnimodal /workspace/dllm/examples/omnimodal` ✅

## Deferred follow-ups
- Integrate concrete image/video/audio/pdf tokenizer backends via adapter registry.
- Wire omnimodal hooks into specific pipeline trainer entry scripts under feature flags.
