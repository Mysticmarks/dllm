# /workspace/dllm/examples/omnimodal/README.md

## Quick start

```bash
source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
python /workspace/dllm/examples/omnimodal/validate_manifest.py --manifest /workspace/dllm/examples/omnimodal/sample_manifest.jsonl
```

## Notes
- This example validates mixed labeled/unlabeled manifest entries.
- Training integration is intentionally minimal and experimental.
