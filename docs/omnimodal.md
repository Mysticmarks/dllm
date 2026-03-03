# /workspace/dllm/docs/omnimodal.md

## Omnimodal foundation (experimental)

This document describes the additive omnimodal foundation introduced under `/workspace/dllm/dllm/omnimodal`.

### Backward compatibility
- Existing text-only workflows remain unchanged unless you explicitly opt into omnimodal configs.

### Current support matrix
- Ingestion routing: txt/md/pdf/jpg/jpeg/png/webp/gif/mp4/avi/webm/mp3/wav/flac/mid/midi.
- Text tokenization: functional via wrapped tokenizer adapter.
- MIDI tokenization: minimally functional byte/event-style adapter.
- Image/video/audio/pdf tokenization: stub adapters with explicit backend configuration errors.

### Main components
- Contracts: `/workspace/dllm/dllm/omnimodal/contracts.py`
- Detection: `/workspace/dllm/dllm/omnimodal/detection.py`
- Manifest schema: `/workspace/dllm/dllm/omnimodal/manifest.py`
- Ingestion pipeline: `/workspace/dllm/dllm/omnimodal/ingestion.py`
- Adapter registry: `/workspace/dllm/dllm/omnimodal/adapters.py`
- Strategy registry: `/workspace/dllm/dllm/omnimodal/strategies.py`
- Collator: `/workspace/dllm/dllm/omnimodal/collators.py`
- Trainer hooks: `/workspace/dllm/dllm/omnimodal/trainer_hooks.py`
- Sampler: `/workspace/dllm/dllm/omnimodal/sampler.py`

### Config notes
Use `/workspace/dllm/dllm/omnimodal/config.py` and call `OmnimodalConfig.validate()` early to fail fast.

### Known gaps
- Discrete backends for image/video/audio/pdf are not bundled yet.
- PDF adaptive decomposition policy now expands records deterministically into text/image routes; backend extractors are still pending.

### Training/inference hook updates
- Trainer hooks now expose objective-level and modality-level metric mapping helpers for logging integrations.
- Sampler conditioning now validates payload shape and types before inference calls.
