# /workspace/dllm/TODOs.md

## Immediate TODO backlog (synchronized with /workspace/dllm/TASKS.md)

### Phase 0
- [x] Audit architecture and map extension points.
- [x] Finalize typed contracts package (`/workspace/dllm/dllm/omnimodal/contracts.py`).
- [x] Add compatibility shim notes for existing text paths.

### Phase 1
- [x] Build modality detector with extension + MIME + sanity parser checks.
- [x] Add deterministic folder scanner for mixed assets.
- [x] Implement bad-sample quarantine JSONL writer.
- [x] Add skip/retry policy abstraction.

### Phase 2
- [x] Add tokenization adapter protocol and registry.
- [x] Wrap existing text tokenizer as `TextTokenizationAdapter`.
- [x] Add image/video/audio/pdf stub adapters with actionable backend errors.
- [x] Add minimally functional MIDI event tokenizer adapter.

### Phase 3
- [x] Add manifest schema and JSONL parser/validator.
- [x] Support labeled/unlabeled/weak labels in one schema.
- [x] Add grouped sample linkage and alignment metadata.
- [x] Add PDF adaptive routing policy (`auto`, `text_only`, `image_only`, `hybrid`).

### Phase 4
- [x] Implement unified token package schema.
- [x] Add mixed-batch collator with max-token-budget mode.
- [ ] Add weighted modality/source sampler and curriculum schedule hooks.
- [x] Add objective strategy registry and deterministic routing trace.

### Phase 5
- [x] Implement trainer hook mixin for modality-aware preprocess/loss.
- [x] Add per-modality and per-objective metric logging.
- [ ] Keep existing trainers untouched unless hooks explicitly enabled.

### Phase 6
- [x] Implement minimal omnimodal sampler entry point.
- [x] Add conditioning validation and unsupported decode failure messages.

### Phase 7
- [x] Add `/workspace/dllm/docs/omnimodal.md`.
- [x] Add `/workspace/dllm/examples/omnimodal/*` configs/manifests.
- [x] Add tests for detection/manifest/adapters/collator/strategy/trainer hooks.

### Phase 8
- [ ] Run broad test suite and text backward-compat smoke.
- [ ] Run mixed ingestion smoke with temporary synthetic dataset.
- [x] Finalize `IMPLEMENTATION_SUMMARY.md`.

## Parallel-safe bundles
- Bundle A: Manifest schema + tests.
- Bundle B: Adapter contracts + registry + stub tests.
- Bundle C: Scanner/quarantine + detection tests.
- Bundle D: Docs/examples independent of trainer internals.

## Rollback checklist
- [ ] Keep feature flags default-off for new modality paths.
- [ ] Isolate omnimodal imports to avoid import-time failures.
- [ ] Separate trainer hooks from base trainer classes.

## Open blocker tracker
- [ ] External discrete tokenizer backends are not bundled yet (image/video/audio).
- [ ] Need policy finalization for GIF frame-threshold defaults.
