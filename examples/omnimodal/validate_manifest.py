"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python /workspace/dllm/examples/omnimodal/validate_manifest.py --manifest /workspace/dllm/examples/omnimodal/sample_manifest.jsonl
"""

import argparse

from dllm.omnimodal.manifest import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    records = load_manifest(args.manifest)
    print(f"validated_records={len(records)}")
    modalities = sorted({record.modality.value for record in records})
    print("modalities=", ",".join(modalities))


if __name__ == "__main__":
    main()
